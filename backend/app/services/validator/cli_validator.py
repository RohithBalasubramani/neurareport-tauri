# mypy: ignore-errors
"""
Claude CLI validator — runs Claude Code CLI (with Qwen 3.5 27B) to analyze
validation results and visually inspect generated reports.

Architecture:
1. Python runs deterministic checks + dry run → produces results JSON + PDF
2. Claude CLI (--bare) gets results + PDF image → makes final judgment
3. For vision: direct LiteLLM call (Claude CLI can't pass images in --bare mode)

This keeps Claude CLI in the loop as the decision-maker while Python does the
heavy lifting of actual validation.
"""
from __future__ import annotations

import base64
import json
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from .models import Severity, ValidationIssue, ValidationResult

logger = logging.getLogger("neura.validator.cli")


def _get_claude_bin() -> str:
    """Find the claude CLI binary."""
    import shutil
    claude = shutil.which("claude")
    if claude:
        return claude
    for p in [
        Path.home() / ".local" / "bin" / "claude",
        Path("/usr/local/bin/claude"),
    ]:
        if p.is_file():
            return str(p)
    raise RuntimeError("Claude CLI not found")


def _get_litellm_config():
    """Get LiteLLM proxy URL and key from LLMConfig."""
    try:
        from backend.app.services.llm import get_llm_config
        config = get_llm_config()
        return (
            getattr(config, 'api_base', 'http://localhost:4000').rstrip('/'),
            getattr(config, 'api_key', 'dummy') or 'dummy',
        )
    except Exception:
        return 'http://localhost:4000', 'dummy'


def cli_analyze_results(
    validation_json: dict,
    template_dir: Path,
) -> list[ValidationIssue]:
    """
    Pass validation results to Claude CLI (with Qwen) for analysis.
    Returns LLM-generated issues/recommendations.
    """
    issues: list[ValidationIssue] = []
    api_base, api_key = _get_litellm_config()

    # Build prompt with validation results
    prompt = f"""You are a NeuraReport pipeline validator. Analyze these validation results and provide your verdict.

VALIDATION RESULTS:
{json.dumps(validation_json, indent=2)}

TEMPLATE DIRECTORY: {template_dir}

Respond with EXACTLY this JSON format (no markdown, no commentary):
{{"verdict": "PASS" or "FAIL", "analysis": "brief explanation", "critical_fixes": ["fix1", "fix2"]}}"""

    try:
        claude_bin = _get_claude_bin()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        import os
        env = os.environ.copy()
        env.pop('CLAUDECODE', None)
        env['ANTHROPIC_BASE_URL'] = api_base
        env['ANTHROPIC_API_KEY'] = api_key

        t0 = time.time()
        with open(prompt_file, 'r') as pf:
            result = subprocess.run(
                [claude_bin, "-p", "--bare", "--model", os.getenv("LLM_MODEL", "qwen")],
                stdin=pf,
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )

        os.unlink(prompt_file)
        elapsed = time.time() - t0
        content = result.stdout.strip()

        logger.info(f"cli_analyze elapsed={elapsed:.1f}s output_len={len(content)}")

        if not content:
            issues.append(ValidationIssue(
                severity=Severity.WARNING, category="cli_analysis",
                message="Claude CLI returned empty analysis",
            ))
            return issues

        # Parse JSON from response
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        data = json.loads(cleaned)
        verdict = data.get("verdict", "UNKNOWN")
        analysis = data.get("analysis", "")
        fixes = data.get("critical_fixes", [])

        sev = Severity.INFO if verdict == "PASS" else Severity.ERROR
        issues.append(ValidationIssue(
            severity=sev, category="cli_analysis",
            message=f"Claude CLI verdict: {verdict} — {analysis}",
        ))

        for fix in fixes:
            issues.append(ValidationIssue(
                severity=Severity.WARNING, category="cli_fix",
                message=f"Recommended fix: {fix}",
            ))

    except json.JSONDecodeError:
        issues.append(ValidationIssue(
            severity=Severity.INFO, category="cli_analysis",
            message=f"Claude CLI analysis (raw): {content[:300]}",
        ))
    except Exception as exc:
        issues.append(ValidationIssue(
            severity=Severity.WARNING, category="cli_analysis",
            message=f"Claude CLI analysis failed: {exc}",
        ))

    return issues


def cli_visual_inspect(
    pdf_path: Path,
    contract: dict,
) -> list[ValidationIssue]:
    """
    Send the dry-run PDF to Qwen 3.5 27B (via LiteLLM vision) for visual inspection.
    Uses direct HTTP (not Claude CLI) because --bare mode can't pass images.
    """
    issues: list[ValidationIssue] = []
    api_base, api_key = _get_litellm_config()

    try:
        import fitz
        import requests

        doc = fitz.open(str(pdf_path))
        if len(doc) == 0:
            issues.append(ValidationIssue(
                severity=Severity.ERROR, category="visual",
                message="Generated PDF has 0 pages",
            ))
            doc.close()
            return issues

        pix = doc[0].get_pixmap(dpi=200)
        b64_image = base64.b64encode(pix.tobytes("png")).decode()
        doc.close()

        tokens = contract.get("tokens", {})
        expected_cols = tokens.get("row_tokens", [])
        expected_scalars = tokens.get("scalars", [])

        prompt = f"""You are a report quality inspector. Examine this generated report and check:
1. HEADER: Company name and report title visible?
2. TABLE: Column headers present? Data rows with actual values (numbers/dates)?
3. TOKEN LEAKS: Any visible {{placeholder}} or {{{{token}}}} text that should be data?
4. LAYOUT: Clean layout, no overlapping text, no broken borders?
5. BLANK AREAS: Large empty sections where data should be?

Expected columns: {', '.join(expected_cols[:8])}
Expected headers: {', '.join(expected_scalars)}

Return ONLY JSON: {{"passed": true/false, "issues": [{{"severity": "error/warning", "message": "..."}}]}}"""

        t0 = time.time()
        resp = requests.post(
            f"{api_base}/v1/messages",
            json={
                "model": os.getenv("LLM_MODEL", "qwen"),
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "source": {
                            "type": "base64", "media_type": "image/png", "data": b64_image,
                        }},
                    ],
                }],
            },
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=180,
        )
        elapsed = time.time() - t0

        data = resp.json()
        if "error" in data:
            issues.append(ValidationIssue(
                severity=Severity.WARNING, category="visual",
                message=f"Vision call failed: {data['error']}",
            ))
            return issues

        raw_text = data.get("content", [{}])[0].get("text", "")
        logger.info(f"cli_visual_inspect elapsed={elapsed:.1f}s")

        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        result = json.loads(cleaned)
        for li in result.get("issues", []):
            sev = Severity.ERROR if li.get("severity") == "error" else Severity.WARNING
            issues.append(ValidationIssue(
                severity=sev, category="visual",
                message=li.get("message", "Visual issue"),
            ))

        if result.get("passed") and not result.get("issues"):
            issues.append(ValidationIssue(
                severity=Severity.INFO, category="visual",
                message="Visual inspection passed — report looks correct",
            ))

    except json.JSONDecodeError:
        issues.append(ValidationIssue(
            severity=Severity.INFO, category="visual",
            message=f"Visual inspection (raw): {raw_text[:200] if 'raw_text' in dir() else 'no response'}",
        ))
    except Exception as exc:
        issues.append(ValidationIssue(
            severity=Severity.WARNING, category="visual",
            message=f"Visual inspection failed: {exc}",
        ))

    return issues
