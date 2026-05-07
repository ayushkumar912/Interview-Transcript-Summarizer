# Interview Transcript Summarizer

A minimal Python CLI tool that reads an interview transcript text file and returns a structured recruiter-style summary using the Google Gemini API.

The implementation is intentionally simple: one transcript in, one Gemini request, validated JSON out.

## Project Structure

```text
.
├── summarizer.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── prompt_iterations.md
├── sample_outputs.md
├── sample_transcript_assignment_1.txt
├── sample_transcript_assignment_2.txt
└── outputs/
    ├── sample_transcript_assignment_1_summary.json
    └── sample_transcript_assignment_2_summary.json
```

## Output Schema

The CLI prints formatted JSON to stdout and can also save the same JSON to a file with `--output`.

```json
{
  "topics_covered": [
    "topic 1",
    "topic 2"
  ],
  "profile": {
    "role": "",
    "level": "",
    "justification": ""
  },
  "candidate_summary": ""
}
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Gemini API Key

Create an API key from Google AI Studio:

1. Open https://aistudio.google.com/
2. Sign in with a Google account.
3. Create an API key.
4. Keep the key private.
5. Do not commit real API keys.

Copy the environment template:

```bash
cp .env.example .env
```

Set your key in `.env`:

```bash
GEMINI_API_KEY=your_real_api_key_here
```

The CLI loads `.env` automatically with `python-dotenv`.

## Usage

Run with the default assignment model, `gemini-2.0-flash`:

```bash
python summarizer.py path/to/transcript.txt
```

Save JSON to a file:

```bash
python summarizer.py path/to/transcript.txt --output outputs/summary.json
```

Use a different Gemini model when your API project has quota limitations:

```bash
python summarizer.py path/to/transcript.txt --model gemini-2.5-flash-lite
```

You can also set the model through an environment variable:

```bash
GEMINI_MODEL=gemini-2.5-flash-lite
```

## Sample Runs

This repo includes two sample transcripts:

- `sample_transcript_assignment_1.txt`
- `sample_transcript_assignment_2.txt`

Run and save both sample outputs:

```bash
python summarizer.py sample_transcript_assignment_1.txt \
  --model gemini-2.5-flash-lite \
  --output outputs/sample_transcript_assignment_1_summary.json

python summarizer.py sample_transcript_assignment_2.txt \
  --model gemini-2.5-flash-lite \
  --output outputs/sample_transcript_assignment_2_summary.json
```

Saved sample JSON files:

- `outputs/sample_transcript_assignment_1_summary.json`
- `outputs/sample_transcript_assignment_2_summary.json`

Markdown copies of sample outputs are available in `sample_outputs.md`.

## Model and Provider Choice

The assignment default is Google Gemini `gemini-2.0-flash`, called through the official `google-genai` SDK.

`gemini-2.0-flash` is appropriate for this task because transcript summarization is a deterministic extraction problem, not a retrieval or agent workflow. The request uses:

- `temperature=0.2`
- `response_mime_type="application/json"`
- `response_json_schema` for structured output
- local JSON validation before printing or saving

The optional `--model` flag is included only for operational flexibility when a Gemini API project does not have quota for the default model.

## Implementation Notes

The code is contained in `summarizer.py` and uses these functions:

- `load_transcript()` reads the transcript file.
- `build_prompt()` creates the recruiter-style extraction prompt.
- `generate_summary()` calls Gemini once.
- `validate_response()` parses and validates the JSON response.
- `main()` handles CLI arguments, output printing, and optional file writing.

The project does not use LangChain, agents, vector databases, embeddings, or RAG.

## Prompt Behavior

The prompt asks Gemini to:

- infer major interview themes
- infer likely role and seniority from evidence
- provide a concise justification
- avoid inventing experience or seniority
- state uncertainty when evidence is weak
- return valid JSON only

Prompt development notes are documented in `prompt_iterations.md`.

## Error Handling

The CLI handles common failures:

- missing transcript file
- empty transcript file
- non-UTF-8 transcript text
- missing `GEMINI_API_KEY`
- Gemini API errors
- invalid or malformed JSON responses

Errors are printed to stderr and the command exits with status code `1`.

## Reflection

The main design tradeoff is using one strong prompt instead of a larger pipeline. That keeps the project easy to review, avoids unnecessary infrastructure, and matches the assignment requirement to prefer a single API call.

The schema validation is intentionally lightweight. It verifies shape and required fields, while leaving the LLM responsible for the semantic quality of the summary.

## Limitations

- Very long transcripts may exceed model input limits.
- Summary quality depends on transcript quality.
- JSON validation checks structure, not factual perfection.
- Role and seniority inference should be treated as recruiter-supporting context, not a hiring decision.
- API quota depends on the selected Gemini model and Google project configuration.
# -
