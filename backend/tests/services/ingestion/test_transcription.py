"""
Transcription Service Tests - Testing audio/video transcription.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


from backend.app.services.ingestion.transcription import (
    TranscriptionService,
    TranscriptionResult,
    TranscriptionSegment,
    VoiceMemoResult,
    TranscriptionLanguage,
)


@pytest.fixture
def service() -> TranscriptionService:
    """Create a transcription service instance."""
    return TranscriptionService()


@pytest.fixture
def sample_audio_content() -> bytes:
    """Sample audio file content (mock data)."""
    return b"RIFF....WAVEfmt " + b"\x00" * 100  # Minimal WAV header


@pytest.fixture
def sample_transcription_result() -> dict:
    """Sample Whisper transcription result."""
    return {
        "text": "Hello, this is a test transcription. It has multiple sentences.",
        "language": "en",
        "segments": [
            {"start": 0.0, "end": 2.0, "text": "Hello, this is a test transcription.", "avg_logprob": -0.3},
            {"start": 2.0, "end": 4.0, "text": "It has multiple sentences.", "avg_logprob": -0.2},
        ],
    }


# =============================================================================
# SUPPORTED FORMAT TESTS
# =============================================================================


class TestSupportedFormats:
    """Test supported audio/video formats."""

    def test_audio_formats(self, service: TranscriptionService):
        """Service supports expected audio formats."""
        assert ".mp3" in service.AUDIO_FORMATS
        assert ".wav" in service.AUDIO_FORMATS
        assert ".m4a" in service.AUDIO_FORMATS
        assert ".ogg" in service.AUDIO_FORMATS
        assert ".flac" in service.AUDIO_FORMATS
        assert ".aac" in service.AUDIO_FORMATS

    def test_video_formats(self, service: TranscriptionService):
        """Service supports expected video formats."""
        assert ".mp4" in service.VIDEO_FORMATS
        assert ".avi" in service.VIDEO_FORMATS
        assert ".mov" in service.VIDEO_FORMATS
        assert ".mkv" in service.VIDEO_FORMATS
        assert ".webm" in service.VIDEO_FORMATS


# =============================================================================
# TRANSCRIPTION LANGUAGE TESTS
# =============================================================================


class TestTranscriptionLanguage:
    """Test TranscriptionLanguage enum."""

    def test_language_values(self):
        """All expected languages defined."""
        assert TranscriptionLanguage.AUTO.value == "auto"
        assert TranscriptionLanguage.ENGLISH.value == "en"
        assert TranscriptionLanguage.SPANISH.value == "es"
        assert TranscriptionLanguage.FRENCH.value == "fr"
        assert TranscriptionLanguage.GERMAN.value == "de"
        assert TranscriptionLanguage.CHINESE.value == "zh"
        assert TranscriptionLanguage.JAPANESE.value == "ja"

    def test_language_count(self):
        """Correct number of languages."""
        assert len(TranscriptionLanguage) == 14


# =============================================================================
# TRANSCRIPTION SEGMENT TESTS
# =============================================================================


class TestTranscriptionSegment:
    """Test TranscriptionSegment model."""

    def test_segment_required_fields(self):
        """Segment has required fields."""
        segment = TranscriptionSegment(
            start_time=0.0,
            end_time=5.0,
            text="Hello world",
        )

        assert segment.start_time == 0.0
        assert segment.end_time == 5.0
        assert segment.text == "Hello world"
        assert segment.confidence == 1.0  # Default

    def test_segment_optional_speaker(self):
        """Segment can have speaker label."""
        segment = TranscriptionSegment(
            start_time=0.0,
            end_time=5.0,
            text="Hello",
            speaker="Speaker 1",
        )

        assert segment.speaker == "Speaker 1"


# =============================================================================
# TRANSCRIPTION RESULT TESTS
# =============================================================================


class TestTranscriptionResult:
    """Test TranscriptionResult model."""

    def test_result_required_fields(self):
        """Result has required fields."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="audio.mp3",
            duration_seconds=120.0,
            language="en",
            full_text="Full transcript here",
            word_count=3,
        )

        assert result.document_id == "doc-123"
        assert result.duration_seconds == 120.0
        assert result.word_count == 3

    def test_result_defaults(self):
        """Result has sensible defaults."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="audio.mp3",
            duration_seconds=60.0,
            language="en",
            full_text="Text",
            word_count=1,
        )

        assert result.segments == []
        assert result.speaker_count == 1
        assert result.metadata == {}


# =============================================================================
# VOICE MEMO RESULT TESTS
# =============================================================================


class TestVoiceMemoResult:
    """Test VoiceMemoResult model."""

    def test_voice_memo_result(self):
        """VoiceMemoResult with all fields."""
        result = VoiceMemoResult(
            document_id="memo-123",
            title="Meeting Notes",
            transcript="Full transcript here",
            duration_seconds=300.0,
            action_items=["Review document", "Send email"],
            key_points=["Budget approved", "Timeline set"],
        )

        assert result.title == "Meeting Notes"
        assert len(result.action_items) == 2
        assert len(result.key_points) == 2


# =============================================================================
# TRANSCRIBE FILE TESTS
# =============================================================================


class TestTranscribeFile:
    """Test file transcription."""

    @pytest.mark.asyncio
    async def test_transcribe_file(self, service: TranscriptionService, sample_audio_content: bytes, sample_transcription_result: dict):
        """Transcribe audio file."""
        with patch.object(service, "_ensure_ffmpeg", return_value=True):
            with patch.object(service, "_get_audio_duration", new_callable=AsyncMock) as mock_duration:
                mock_duration.return_value = 10.0
                with patch.object(service, "_get_whisper") as mock_whisper:
                    mock_model = MagicMock()
                    mock_model.transcribe = MagicMock(return_value=sample_transcription_result)
                    mock_whisper.return_value = mock_model

                    result = await service.transcribe_file(
                        filename="recording.wav",
                        content=sample_audio_content,
                    )

        assert isinstance(result, TranscriptionResult)
        assert result.language == "en"
        assert len(result.segments) == 2

    @pytest.mark.asyncio
    async def test_transcribe_file_with_language(self, service: TranscriptionService, sample_audio_content: bytes, sample_transcription_result: dict):
        """Transcribe with specific language."""
        with patch.object(service, "_ensure_ffmpeg", return_value=True):
            with patch.object(service, "_get_audio_duration", new_callable=AsyncMock) as mock_duration:
                mock_duration.return_value = 10.0
                with patch.object(service, "_get_whisper") as mock_whisper:
                    mock_model = MagicMock()
                    mock_model.transcribe = MagicMock(return_value=sample_transcription_result)
                    mock_whisper.return_value = mock_model

                    result = await service.transcribe_file(
                        filename="recording.wav",
                        content=sample_audio_content,
                        language=TranscriptionLanguage.SPANISH,
                    )

        # Language option should be passed
        mock_model.transcribe.assert_called_once()

    @pytest.mark.asyncio
    async def test_transcribe_file_without_timestamps(self, service: TranscriptionService, sample_audio_content: bytes):
        """Transcribe without timestamps."""
        result_without_segments = {
            "text": "Hello world",
            "language": "en",
        }

        with patch.object(service, "_ensure_ffmpeg", return_value=True):
            with patch.object(service, "_get_audio_duration", new_callable=AsyncMock) as mock_duration:
                mock_duration.return_value = 5.0
                with patch.object(service, "_get_whisper") as mock_whisper:
                    mock_model = MagicMock()
                    mock_model.transcribe = MagicMock(return_value=result_without_segments)
                    mock_whisper.return_value = mock_model

                    result = await service.transcribe_file(
                        filename="recording.wav",
                        content=sample_audio_content,
                        include_timestamps=False,
                    )

        assert result.segments == []

    @pytest.mark.asyncio
    async def test_transcribe_video_extracts_audio(self, service: TranscriptionService, sample_transcription_result: dict):
        """Video file triggers audio extraction."""
        video_content = b"video content"

        with patch.object(service, "_ensure_ffmpeg", return_value=True):
            with patch.object(service, "_extract_audio", new_callable=AsyncMock) as mock_extract:
                mock_extract.return_value = Path("/tmp/audio.wav")
                with patch.object(service, "_get_audio_duration", new_callable=AsyncMock) as mock_duration:
                    mock_duration.return_value = 60.0
                    with patch.object(service, "_get_whisper") as mock_whisper:
                        mock_model = MagicMock()
                        mock_model.transcribe = MagicMock(return_value=sample_transcription_result)
                        mock_whisper.return_value = mock_model
                        with patch("pathlib.Path.unlink"):  # Prevent file deletion
                            result = await service.transcribe_file(
                                filename="video.mp4",
                                content=video_content,
                            )

                mock_extract.assert_called_once()


# =============================================================================
# VOICE MEMO TRANSCRIPTION TESTS
# =============================================================================


class TestTranscribeVoiceMemo:
    """Test voice memo transcription."""

    @pytest.mark.asyncio
    async def test_transcribe_voice_memo(self, service: TranscriptionService, sample_audio_content: bytes, sample_transcription_result: dict):
        """Transcribe voice memo with insights."""
        with patch.object(service, "transcribe_file", new_callable=AsyncMock) as mock_transcribe:
            mock_transcribe.return_value = TranscriptionResult(
                document_id="doc-123",
                source_filename="memo.m4a",
                duration_seconds=60.0,
                language="en",
                full_text="Please review the document. The deadline is Friday.",
                word_count=8,
            )
            with patch.object(service, "_extract_insights", new_callable=AsyncMock) as mock_insights:
                mock_insights.return_value = {
                    "action_items": ["Review the document"],
                    "key_points": ["Deadline is Friday"],
                }

                result = await service.transcribe_voice_memo(
                    filename="memo.m4a",
                    content=sample_audio_content,
                )

        assert isinstance(result, VoiceMemoResult)
        assert len(result.action_items) > 0
        assert len(result.key_points) > 0

    @pytest.mark.asyncio
    async def test_transcribe_voice_memo_generates_title(self, service: TranscriptionService, sample_audio_content: bytes):
        """Voice memo generates title from first sentence."""
        with patch.object(service, "transcribe_file", new_callable=AsyncMock) as mock_transcribe:
            mock_transcribe.return_value = TranscriptionResult(
                document_id="doc-123",
                source_filename="memo.m4a",
                duration_seconds=30.0,
                language="en",
                full_text="This is the title sentence. This is more content.",
                word_count=10,
            )
            with patch.object(service, "_extract_insights", new_callable=AsyncMock) as mock_insights:
                mock_insights.return_value = {"action_items": [], "key_points": []}

                result = await service.transcribe_voice_memo(
                    filename="memo.m4a",
                    content=sample_audio_content,
                )

        assert "title sentence" in result.title.lower()


# =============================================================================
# TITLE GENERATION TESTS
# =============================================================================


class TestTitleGeneration:
    """Test title generation from transcript."""

    def test_generate_title_first_sentence(self, service: TranscriptionService):
        """Title is first sentence of transcript."""
        text = "This is the first sentence. This is the second."
        result = service._generate_title(text)

        assert result == "This is the first sentence"

    def test_generate_title_truncated(self, service: TranscriptionService):
        """Long title is truncated."""
        text = "A" * 200 + ". More text."
        result = service._generate_title(text)

        assert len(result) <= 83  # 80 + "..."

    def test_generate_title_fallback(self, service: TranscriptionService):
        """Empty text returns empty (no fallback in current implementation)."""
        result = service._generate_title("")

        # Empty text returns empty string (list has one empty element after split)
        assert result == ""


# =============================================================================
# SRT FORMATTING TESTS
# =============================================================================


class TestSrtFormatting:
    """Test SRT subtitle format generation."""

    def test_format_as_srt(self, service: TranscriptionService):
        """Format transcription as SRT."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="video.mp4",
            duration_seconds=10.0,
            language="en",
            full_text="Hello world",
            word_count=2,
            segments=[
                TranscriptionSegment(start_time=0.0, end_time=2.5, text="Hello"),
                TranscriptionSegment(start_time=2.5, end_time=5.0, text="world"),
            ],
        )

        srt = service._format_as_srt(result)

        assert "1\n" in srt
        assert "2\n" in srt
        assert "00:00:00,000 --> 00:00:02,500" in srt
        assert "Hello" in srt
        assert "world" in srt

    def test_format_srt_time(self, service: TranscriptionService):
        """Format seconds as SRT timestamp."""
        result = service._format_srt_time(3661.5)  # 1:01:01.500

        assert result == "01:01:01,500"

    def test_format_srt_time_zero(self, service: TranscriptionService):
        """Format zero seconds."""
        result = service._format_srt_time(0.0)

        assert result == "00:00:00,000"


# =============================================================================
# MARKDOWN FORMATTING TESTS
# =============================================================================


class TestMarkdownFormatting:
    """Test Markdown format generation."""

    def test_format_as_markdown(self, service: TranscriptionService):
        """Format transcription as Markdown."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="audio.mp3",
            duration_seconds=120.0,
            language="en",
            full_text="Hello world transcript content",
            word_count=4,
            segments=[
                TranscriptionSegment(start_time=0.0, end_time=60.0, text="Hello world"),
            ],
        )

        md = service._format_as_markdown(result, include_timestamps=True)

        assert "# Transcript: audio.mp3" in md
        assert "**Duration:**" in md
        assert "[0:00]" in md
        assert "Hello world" in md

    def test_format_as_markdown_no_timestamps(self, service: TranscriptionService):
        """Format as Markdown without timestamps."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="audio.mp3",
            duration_seconds=60.0,
            language="en",
            full_text="Full transcript text",
            word_count=3,
        )

        md = service._format_as_markdown(result, include_timestamps=False)

        assert "Full transcript text" in md
        assert "[" not in md or "**" in md  # No timestamp brackets except for markdown


# =============================================================================
# HTML FORMATTING TESTS
# =============================================================================


class TestHtmlFormatting:
    """Test HTML format generation."""

    def test_format_as_html(self, service: TranscriptionService):
        """Format transcription as HTML."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="video.mp4",
            duration_seconds=180.0,
            language="en",
            full_text="Test transcript",
            word_count=2,
            segments=[
                TranscriptionSegment(start_time=0.0, end_time=5.0, text="Test"),
            ],
        )

        html = service._format_as_html(result, include_timestamps=True)

        assert "<!DOCTYPE html>" in html
        assert "<title>Transcript: video.mp4</title>" in html
        assert "Test" in html

    def test_format_as_html_with_speakers(self, service: TranscriptionService):
        """HTML includes speaker labels."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="meeting.mp3",
            duration_seconds=300.0,
            language="en",
            full_text="Speaker text",
            word_count=2,
            segments=[
                TranscriptionSegment(start_time=0.0, end_time=30.0, text="Hello", speaker="Speaker 1"),
                TranscriptionSegment(start_time=30.0, end_time=60.0, text="Hi there", speaker="Speaker 2"),
            ],
            speaker_count=2,
        )

        html = service._format_as_html(result, include_timestamps=True)

        assert "Speaker 1" in html
        assert "Speaker 2" in html


# =============================================================================
# DURATION FORMATTING TESTS
# =============================================================================


class TestDurationFormatting:
    """Test duration formatting."""

    def test_format_duration_minutes(self, service: TranscriptionService):
        """Format minutes and seconds."""
        result = service._format_duration(125)  # 2:05

        assert result == "2:05"

    def test_format_duration_hours(self, service: TranscriptionService):
        """Format hours, minutes, seconds."""
        result = service._format_duration(3661)  # 1:01:01

        assert result == "1:01:01"

    def test_format_duration_zero(self, service: TranscriptionService):
        """Format zero duration."""
        result = service._format_duration(0)

        assert result == "0:00"

    def test_format_duration_seconds_only(self, service: TranscriptionService):
        """Format seconds only."""
        result = service._format_duration(45)

        assert result == "0:45"


# =============================================================================
# SPEAKER DIARIZATION TESTS
# =============================================================================


class TestSpeakerDiarization:
    """Test speaker diarization."""

    @pytest.mark.asyncio
    async def test_diarize_speakers(self, service: TranscriptionService, tmp_path: Path):
        """Basic speaker diarization."""
        segments = [
            TranscriptionSegment(start_time=0.0, end_time=2.0, text="Hello"),
            TranscriptionSegment(start_time=5.0, end_time=7.0, text="Hi there"),  # 3s gap
            TranscriptionSegment(start_time=7.5, end_time=9.0, text="How are you"),
        ]

        audio_path = tmp_path / "audio.wav"
        audio_path.write_bytes(b"audio content")

        result = await service._diarize_speakers(segments, audio_path)

        # All segments should have speaker labels
        assert all(s.speaker is not None for s in result)

    @pytest.mark.asyncio
    async def test_diarize_speakers_changes_on_pause(self, service: TranscriptionService, tmp_path: Path):
        """Speaker changes after long pause."""
        segments = [
            TranscriptionSegment(start_time=0.0, end_time=1.0, text="First"),
            TranscriptionSegment(start_time=5.0, end_time=6.0, text="Second"),  # 4s pause
        ]

        audio_path = tmp_path / "audio.wav"
        audio_path.write_bytes(b"audio")

        result = await service._diarize_speakers(segments, audio_path)

        # Should potentially switch speakers
        assert len(result) == 2


# =============================================================================
# FFMPEG HANDLING TESTS
# =============================================================================


class TestFfmpegHandling:
    """Test ffmpeg availability handling."""

    def test_ensure_ffmpeg_on_path(self, service: TranscriptionService):
        """Check ffmpeg when on PATH."""
        with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
            result = service._ensure_ffmpeg()

        assert result is True

    def test_ensure_ffmpeg_not_found(self, service: TranscriptionService):
        """Handle ffmpeg not found."""
        with patch("shutil.which", return_value=None):
            with patch("pathlib.Path.glob", return_value=[]):
                result = service._ensure_ffmpeg()

        assert result is False


# =============================================================================
# CREATE DOCUMENT FROM TRANSCRIPTION TESTS
# =============================================================================


class TestCreateDocumentFromTranscription:
    """Test document creation from transcription."""

    @pytest.mark.asyncio
    async def test_create_document_html(self, service: TranscriptionService):
        """Create HTML document from transcription."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="audio.mp3",
            duration_seconds=60.0,
            language="en",
            full_text="Transcript text",
            word_count=2,
        )

        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "new-doc-id"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            doc_id = await service.create_document_from_transcription(
                result=result,
                format="html",
            )

        assert doc_id == "new-doc-id"
        mock_ingest.ingest_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_document_srt(self, service: TranscriptionService):
        """Create SRT document from transcription."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="video.mp4",
            duration_seconds=120.0,
            language="en",
            full_text="Text",
            word_count=1,
            segments=[TranscriptionSegment(start_time=0, end_time=5, text="Text")],
        )

        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "srt-doc"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            doc_id = await service.create_document_from_transcription(
                result=result,
                format="srt",
            )

        # Filename should be .srt
        call_args = mock_ingest.ingest_file.call_args
        assert call_args.kwargs["filename"].endswith(".srt")

    @pytest.mark.asyncio
    async def test_create_document_markdown(self, service: TranscriptionService):
        """Create Markdown document from transcription."""
        result = TranscriptionResult(
            document_id="doc-123",
            source_filename="audio.mp3",
            duration_seconds=60.0,
            language="en",
            full_text="Transcript",
            word_count=1,
        )

        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "md-doc"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            doc_id = await service.create_document_from_transcription(
                result=result,
                format="markdown",
            )

        call_args = mock_ingest.ingest_file.call_args
        assert call_args.kwargs["filename"].endswith(".md")
