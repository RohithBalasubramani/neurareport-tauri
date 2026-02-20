"""
Transcription Service
Handles audio/video transcription for document creation.
"""
from __future__ import annotations

import logging
import os
import shutil
import hashlib
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TranscriptionLanguage(str, Enum):
    """Supported transcription languages."""
    AUTO = "auto"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"


class TranscriptionSegment(BaseModel):
    """A segment of transcription with timing."""
    start_time: float  # Seconds
    end_time: float
    text: str
    confidence: float = 1.0
    speaker: Optional[str] = None


class TranscriptionResult(BaseModel):
    """Result of transcription."""
    document_id: str
    source_filename: str
    duration_seconds: float
    language: str
    segments: List[TranscriptionSegment] = Field(default_factory=list)
    full_text: str
    word_count: int
    speaker_count: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VoiceMemoResult(BaseModel):
    """Result of voice memo transcription."""
    document_id: str
    title: str
    transcript: str
    duration_seconds: float
    action_items: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TranscriptionService:
    """
    Service for transcribing audio and video files.
    Uses Whisper for transcription.
    """

    # Supported audio formats
    AUDIO_FORMATS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".wma"}

    # Supported video formats
    VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".wmv", ".flv"}

    def __init__(self):
        self._whisper_model = None

    def _get_whisper(self):
        """Lazy-load Whisper model."""
        if self._whisper_model is None:
            try:
                import whisper
                self._whisper_model = whisper.load_model("base")
                logger.info("Loaded Whisper base model")
            except ImportError:
                logger.warning("Whisper not installed. Install with: pip install openai-whisper")
                raise RuntimeError("Whisper not installed")
        return self._whisper_model

    def _ensure_ffmpeg(self) -> bool:
        """Ensure ffmpeg is discoverable on PATH for Whisper."""
        if shutil.which("ffmpeg"):
            return True

        backend_root = Path(__file__).resolve().parents[3]
        tools_dir = backend_root / "tools"
        candidates = list(tools_dir.glob("ffmpeg_extracted/**/bin/ffmpeg.exe"))
        if not candidates:
            return False

        bin_dir = candidates[0].parent
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
        return True

    async def transcribe_file(
        self,
        filename: str,
        content: bytes,
        language: TranscriptionLanguage = TranscriptionLanguage.AUTO,
        include_timestamps: bool = True,
        diarize_speakers: bool = False,
    ) -> TranscriptionResult:
        """
        Transcribe an audio or video file.

        Args:
            filename: Original filename
            content: File content
            language: Target language (auto-detect if not specified)
            include_timestamps: Include word/segment timestamps
            diarize_speakers: Attempt to identify different speakers

        Returns:
            TranscriptionResult with full transcript
        """
        self._ensure_ffmpeg()

        # Save to temp file for processing
        ext = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            # Extract audio if video
            if ext in self.VIDEO_FORMATS:
                audio_path = await self._extract_audio(tmp_path)
            else:
                audio_path = tmp_path

            # Get duration
            duration = await self._get_audio_duration(audio_path)

            # Transcribe with Whisper
            model = self._get_whisper()
            options = {
                "task": "transcribe",
                "verbose": False,
            }
            if language != TranscriptionLanguage.AUTO:
                options["language"] = language.value

            result = model.transcribe(str(audio_path), **options)

            # Parse segments
            segments = []
            if include_timestamps and "segments" in result:
                for seg in result["segments"]:
                    segments.append(TranscriptionSegment(
                        start_time=seg["start"],
                        end_time=seg["end"],
                        text=seg["text"].strip(),
                        confidence=seg.get("avg_logprob", 0) + 1,  # Normalize
                    ))

            # Speaker diarization (simplified)
            if diarize_speakers:
                segments = await self._diarize_speakers(segments, audio_path)

            full_text = result["text"].strip()

            # Create document
            doc_id = hashlib.sha256(f"{filename}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16]

            return TranscriptionResult(
                document_id=doc_id,
                source_filename=filename,
                duration_seconds=duration,
                language=result.get("language", "en"),
                segments=segments,
                full_text=full_text,
                word_count=len(full_text.split()),
                speaker_count=len(set(s.speaker for s in segments if s.speaker)) or 1,
                metadata={
                    "model": "whisper-base",
                    "include_timestamps": include_timestamps,
                    "diarize_speakers": diarize_speakers,
                },
            )

        finally:
            # Cleanup temp files
            tmp_path.unlink(missing_ok=True)
            if ext in self.VIDEO_FORMATS:
                audio_path.unlink(missing_ok=True)

    async def transcribe_voice_memo(
        self,
        filename: str,
        content: bytes,
        extract_action_items: bool = True,
        extract_key_points: bool = True,
    ) -> VoiceMemoResult:
        """
        Transcribe a voice memo with intelligent extraction.

        Args:
            filename: Original filename
            content: Audio content
            extract_action_items: Extract TODO/action items
            extract_key_points: Extract key points

        Returns:
            VoiceMemoResult with transcript and extracted items
        """
        # First, get basic transcription
        result = await self.transcribe_file(
            filename=filename,
            content=content,
            include_timestamps=False,
            diarize_speakers=False,
        )

        # Generate title from first sentence
        title = self._generate_title(result.full_text)

        # Extract action items and key points using AI
        action_items = []
        key_points = []

        if extract_action_items or extract_key_points:
            extracted = await self._extract_insights(
                result.full_text,
                extract_action_items=extract_action_items,
                extract_key_points=extract_key_points,
            )
            action_items = extracted.get("action_items", [])
            key_points = extracted.get("key_points", [])

        return VoiceMemoResult(
            document_id=result.document_id,
            title=title,
            transcript=result.full_text,
            duration_seconds=result.duration_seconds,
            action_items=action_items,
            key_points=key_points,
        )

    async def create_document_from_transcription(
        self,
        result: TranscriptionResult,
        format: str = "html",
        include_timestamps: bool = True,
    ) -> str:
        """
        Create a document from transcription result.

        Args:
            result: Transcription result
            format: Output format (html, markdown, srt)
            include_timestamps: Include timestamps in output

        Returns:
            Document ID
        """
        from .service import ingestion_service

        if format == "srt":
            content = self._format_as_srt(result)
            filename = f"{Path(result.source_filename).stem}.srt"
        elif format == "markdown":
            content = self._format_as_markdown(result, include_timestamps)
            filename = f"{Path(result.source_filename).stem}.md"
        else:
            content = self._format_as_html(result, include_timestamps)
            filename = f"{Path(result.source_filename).stem}.html"

        ingestion_result = await ingestion_service.ingest_file(
            filename=filename,
            content=content.encode("utf-8"),
            metadata={
                "source": "transcription",
                "source_file": result.source_filename,
                "duration_seconds": result.duration_seconds,
                "language": result.language,
                "word_count": result.word_count,
            },
        )

        return ingestion_result.document_id

    async def _extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video file."""
        try:
            from moviepy.editor import VideoFileClip

            audio_path = video_path.with_suffix(".wav")
            video = VideoFileClip(str(video_path))
            video.audio.write_audiofile(str(audio_path), verbose=False, logger=None)
            video.close()
            return audio_path
        except ImportError:
            # Fallback to ffmpeg
            import subprocess
            audio_path = video_path.with_suffix(".wav")
            subprocess.run([
                "ffmpeg", "-i", str(video_path),
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                str(audio_path), "-y"
            ], capture_output=True, check=True)
            return audio_path

    async def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio file duration in seconds."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(audio_path))
            return len(audio) / 1000.0
        except ImportError:
            # Fallback using wave module for WAV files
            import wave
            if audio_path.suffix.lower() == ".wav":
                with wave.open(str(audio_path), "r") as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()
                    return frames / float(rate)
            return 0.0

    async def _diarize_speakers(
        self,
        segments: List[TranscriptionSegment],
        audio_path: Path,
    ) -> List[TranscriptionSegment]:
        """Simple speaker diarization based on pauses and patterns."""
        # Simple heuristic: alternate speakers on long pauses
        current_speaker = "Speaker 1"
        speaker_count = 1
        diarized = []

        prev_end = 0
        for seg in segments:
            # If there's a significant pause, potentially switch speakers
            if seg.start_time - prev_end > 2.0:  # 2 second pause
                if speaker_count < 4:  # Max 4 speakers
                    speaker_count += 1
                current_speaker = f"Speaker {((speaker_count - 1) % 2) + 1}"

            diarized.append(TranscriptionSegment(
                start_time=seg.start_time,
                end_time=seg.end_time,
                text=seg.text,
                confidence=seg.confidence,
                speaker=current_speaker,
            ))
            prev_end = seg.end_time

        return diarized

    async def _extract_insights(
        self,
        text: str,
        extract_action_items: bool = True,
        extract_key_points: bool = True,
    ) -> Dict[str, List[str]]:
        """Extract insights from transcript using AI."""
        try:
            from backend.app.services.llm.client import get_llm_client

            client = get_llm_client()

            prompt_parts = []
            if extract_action_items:
                prompt_parts.append("- List any action items, tasks, or TODOs mentioned")
            if extract_key_points:
                prompt_parts.append("- List the key points or main ideas")

            prompt = f"""Analyze this transcript and extract:
{chr(10).join(prompt_parts)}

Transcript:
{text[:4000]}

Respond in JSON format:
{{"action_items": ["item1", "item2"], "key_points": ["point1", "point2"]}}"""

            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="transcription_extract_insights",
                max_tokens=500,
            )

            import json
            content = (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "{}")
            )
            return json.loads(content)

        except Exception as e:
            logger.warning(f"Failed to extract insights: {e}")
            return {"action_items": [], "key_points": []}

    def _generate_title(self, text: str) -> str:
        """Generate a title from transcript text."""
        # Take first sentence
        sentences = text.split(".")
        if sentences:
            title = sentences[0].strip()[:80]
            if len(sentences[0]) > 80:
                title += "..."
            return title
        return "Voice Memo"

    def _format_as_srt(self, result: TranscriptionResult) -> str:
        """Format transcription as SRT subtitle file."""
        lines = []
        for i, seg in enumerate(result.segments, 1):
            start = self._format_srt_time(seg.start_time)
            end = self._format_srt_time(seg.end_time)
            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(seg.text)
            lines.append("")
        return "\n".join(lines)

    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds as SRT timestamp."""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _format_as_markdown(self, result: TranscriptionResult, include_timestamps: bool) -> str:
        """Format transcription as Markdown."""
        lines = [
            f"# Transcript: {result.source_filename}",
            "",
            f"**Duration:** {self._format_duration(result.duration_seconds)}",
            f"**Language:** {result.language}",
            f"**Words:** {result.word_count}",
            "",
            "---",
            "",
        ]

        if include_timestamps and result.segments:
            current_speaker = None
            for seg in result.segments:
                if seg.speaker and seg.speaker != current_speaker:
                    current_speaker = seg.speaker
                    lines.append(f"\n**{current_speaker}:**\n")

                timestamp = self._format_duration(seg.start_time)
                lines.append(f"[{timestamp}] {seg.text}")
        else:
            lines.append(result.full_text)

        return "\n".join(lines)

    def _format_as_html(self, result: TranscriptionResult, include_timestamps: bool) -> str:
        """Format transcription as HTML document."""
        segments_html = ""
        if include_timestamps and result.segments:
            current_speaker = None
            for seg in result.segments:
                speaker_html = ""
                if seg.speaker and seg.speaker != current_speaker:
                    current_speaker = seg.speaker
                    speaker_html = f'<strong class="speaker">{seg.speaker}:</strong><br>'

                timestamp = self._format_duration(seg.start_time)
                segments_html += f"""
                <p class="segment">
                    {speaker_html}
                    <span class="timestamp">[{timestamp}]</span>
                    <span class="text">{seg.text}</span>
                </p>"""
        else:
            segments_html = f"<p>{result.full_text}</p>"

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Transcript: {result.source_filename}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.8;
        }}
        .meta {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .meta span {{
            margin-right: 20px;
            color: #666;
        }}
        .segment {{
            margin: 10px 0;
        }}
        .timestamp {{
            color: #1976d2;
            font-size: 0.85em;
            margin-right: 8px;
        }}
        .speaker {{
            color: #7b1fa2;
        }}
    </style>
</head>
<body>
    <h1>Transcript</h1>
    <div class="meta">
        <span><strong>Source:</strong> {result.source_filename}</span>
        <span><strong>Duration:</strong> {self._format_duration(result.duration_seconds)}</span>
        <span><strong>Language:</strong> {result.language}</span>
        <span><strong>Words:</strong> {result.word_count}</span>
    </div>
    <div class="transcript">
        {segments_html}
    </div>
</body>
</html>"""

    def _format_duration(self, seconds: float) -> str:
        """Format seconds as human-readable duration."""
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"


# Singleton instance
transcription_service = TranscriptionService()
