"""CLI tool for summarizing interview transcripts with Google Gemini."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


DEFAULT_MODEL_NAME = "gemini-2.0-flash"
SUMMARY_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "topics_covered": {
            "type": "array",
            "items": {"type": "string"},
        },
        "profile": {
            "type": "object",
            "properties": {
                "role": {"type": "string"},
                "level": {"type": "string"},
                "justification": {"type": "string"},
            },
            "required": ["role", "level", "justification"],
            "additionalProperties": False,
        },
        "candidate_summary": {"type": "string"},
    },
    "required": ["topics_covered", "profile", "candidate_summary"],
    "additionalProperties": False,
}


class SummarizerError(Exception):
    """Raised for expected CLI errors."""


def load_transcript(file_path: str) -> str:
    """Read a transcript file and return its contents."""
    path = Path(file_path)

    if not path.exists():
        raise SummarizerError(f"Transcript file not found: {path}")
    if not path.is_file():
        raise SummarizerError(f"Transcript path is not a file: {path}")

    try:
        transcript = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SummarizerError("Transcript must be a UTF-8 text file.") from exc
    except OSError as exc:
        raise SummarizerError(f"Could not read transcript: {exc}") from exc

    if not transcript.strip():
        raise SummarizerError("Transcript file is empty.")

    return transcript


def build_prompt(transcript: str) -> str:
    """Build the extraction prompt sent to Gemini."""
    return f"""
You are an experienced technical recruiter summarizing an interview transcript.

Task:
Analyze the transcript and return a concise structured summary for recruiter review.

Output rules:
- Return valid JSON only.
- Do not wrap the JSON in Markdown.
- Do not include commentary before or after the JSON.
- Include exactly these top-level fields: topics_covered, profile, candidate_summary.
- In profile, include exactly these fields: role, level, justification.
- "topics_covered" should list the major interview themes, grouped at a useful level.
- "profile.role" should infer the most likely role from evidence in the transcript.
- "profile.level" should infer likely seniority only when supported by evidence.
- "profile.justification" must cite transcript evidence in concise prose.
- "candidate_summary" should be recruiter-style: concise, useful, and evidence-based.

Reasoning constraints:
- Do not invent employment history, skills, project scope, metrics, education, or seniority.
- If evidence is weak or missing, explicitly state uncertainty in the relevant field.
- Prefer "unclear" over unsupported certainty.
- Base every claim on the transcript only.
- Keep the summary balanced and professional.

Transcript:
\"\"\"
{transcript}
\"\"\"
""".strip()


def generate_summary(
    transcript: str,
    api_key: str | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> dict[str, Any]:
    """Call Gemini and return the validated summary."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise SummarizerError(
            "Missing GEMINI_API_KEY. Set it in your environment or a .env file."
        )

    client = genai.Client(api_key=key)
    prompt = build_prompt(transcript)

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_json_schema=SUMMARY_JSON_SCHEMA,
            ),
        )
    except Exception as exc:
        raise SummarizerError(f"Gemini API request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise SummarizerError("Gemini returned an empty response.")

    return validate_response(text)


def validate_response(response_text: str) -> dict[str, Any]:
    """Parse and validate the Gemini JSON response."""
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise SummarizerError(f"Gemini returned invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise SummarizerError("Gemini response must be a JSON object.")

    required_keys = {"topics_covered", "profile", "candidate_summary"}
    missing_keys = required_keys - data.keys()
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise SummarizerError(f"Gemini response is missing required keys: {missing}")

    topics = data["topics_covered"]
    if not isinstance(topics, list) or not all(isinstance(item, str) for item in topics):
        raise SummarizerError("'topics_covered' must be a list of strings.")

    profile = data["profile"]
    if not isinstance(profile, dict):
        raise SummarizerError("'profile' must be an object.")

    profile_keys = {"role", "level", "justification"}
    missing_profile_keys = profile_keys - profile.keys()
    if missing_profile_keys:
        missing = ", ".join(sorted(missing_profile_keys))
        raise SummarizerError(f"'profile' is missing required keys: {missing}")

    for key in profile_keys:
        if not isinstance(profile[key], str):
            raise SummarizerError(f"'profile.{key}' must be a string.")

    if not isinstance(data["candidate_summary"], str):
        raise SummarizerError("'candidate_summary' must be a string.")

    return {
        "topics_covered": topics,
        "profile": {
            "role": profile["role"],
            "level": profile["level"],
            "justification": profile["justification"],
        },
        "candidate_summary": data["candidate_summary"],
    }


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Summarize an interview transcript with Google Gemini."
    )
    parser.add_argument("transcript", help="Path to the transcript text file.")
    parser.add_argument(
        "--output",
        "-o",
        help="Optional path to save the formatted JSON summary.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("GEMINI_MODEL", DEFAULT_MODEL_NAME),
        help=(
            "Gemini model to use. Defaults to gemini-2.0-flash, "
            "or GEMINI_MODEL if set."
        ),
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    load_dotenv()
    args = parse_args()

    try:
        transcript = load_transcript(args.transcript)
        summary = generate_summary(transcript, model_name=args.model)
        output = json.dumps(summary, indent=2, ensure_ascii=False)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output + "\n", encoding="utf-8")

        print(output)
        return 0
    except SummarizerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
