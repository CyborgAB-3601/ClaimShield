import asyncio
import json
import os
import tempfile
import time
import zipfile
from pathlib import Path

from dotenv import load_dotenv
from sarvamai import SarvamAI

from app.schema import ClaimFormFieldSpec, ExtractedField, ExtractionResult

load_dotenv()

_client: SarvamAI | None = None


def get_client() -> SarvamAI:
    global _client
    if _client is None:
        _client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])
    return _client


def digitise(file_path: str, language: str = "hi-IN") -> str:
    """Run a document through Sarvam Digitise and return the extracted markdown text."""
    client = get_client()
    job = client.document_intelligence.create_job(language=language, output_format="md")
    job.upload_file(file_path)
    job.start()
    job.wait_until_complete(poll_interval=2.0, timeout=180)

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "output.zip"
        job.download_output(str(zip_path))
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmpdir)
            md_files = [n for n in zf.namelist() if n.endswith(".md")]
            if not md_files:
                raise RuntimeError("Digitise output contained no markdown file")
            return (Path(tmpdir) / md_files[0]).read_text(encoding="utf-8")


def _build_extraction_prompt(field_specs: list[ClaimFormFieldSpec]) -> str:
    field_lines = "\n".join(
        f'- "{f.field_key}" ({f.label}, {f.section}): {f.hint}' for f in field_specs
    )
    field_names = ", ".join(f.field_key for f in field_specs)
    return f"""You are extracting structured fields from a digitised Indian hospital discharge summary or \
itemised bill for a health-insurance reimbursement claim. The source text below was produced by \
OCR/handwriting-recognition and may contain errors, gaps, or illegible sections marked as unclear.

Extract exactly these fields:
{field_lines}

Rules (must follow exactly):
1. Only use information explicitly present in the source text. Never infer, guess, or fill in a plausible \
value from general medical/insurance knowledge.
2. If a field is simply not mentioned anywhere in the source text, set "value" to null, "refused" to true, and \
"reason" to "not_present".
3. If a field IS mentioned but the text is unclear, illegible, contradictory, or ambiguous (e.g. OCR marked it \
unclear, handwriting garbled), set "value" to null, "refused" to true, and "reason" to "illegible".
4. For every field you DO extract, give a confidence score from 0.0 to 1.0 reflecting how clearly and \
unambiguously that value appears in the source text, and quote the short "source_line" it came from, and set \
"reason" to null.
5. Respond with strict JSON only, in this exact shape:
{{"fields": [{{"field": "<name>", "value": "<value or null>", "confidence": <0.0-1.0 or null>, \
"refused": <true|false>, "reason": "<not_present|illegible|null>", "source_line": "<quoted source text or null>"}}, ...]}}
One object per field listed above ({field_names}), in the same order.
"""


def _strip_json_fence(text: str) -> str:
    """Sarvam-30B sometimes wraps JSON in ```json fences despite instructions; strip them."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[len("json") :]
    return text.strip()


def extract_fields(markdown_text: str, field_specs: list[ClaimFormFieldSpec]) -> list[ExtractedField]:
    """Prompt Sarvam-30B to pull structured claim fields + confidence out of digitised text.

    field_specs is the dynamic field list derived from the actual uploaded claim form (see
    claim_form_extractor.py) rather than a fixed hardcoded field list.

    Refusal is enforced two ways: the model is instructed to null out anything uncertain,
    and as a safety net any field below CONFIDENCE_THRESHOLD is force-marked refused in code
    regardless of what the model claims.
    """
    client = get_client()
    response = client.chat.completions(
        model="sarvam-30b",
        messages=[
            {"role": "system", "content": _build_extraction_prompt(field_specs)},
            {"role": "user", "content": markdown_text},
        ],
        max_tokens=2048,
        reasoning_effort=None,
    )
    content = response.choices[0].message.content
    parsed = json.loads(_strip_json_fence(content))

    CONFIDENCE_THRESHOLD = 0.5
    results = []
    for raw in parsed.get("fields", []):
        confidence = raw.get("confidence")
        refused = bool(raw.get("refused")) or confidence is None or confidence < CONFIDENCE_THRESHOLD
        raw_value = raw.get("value")
        value = None if refused or raw_value is None else str(raw_value)
        reason = raw.get("reason")
        status = "filled" if not refused else ("missing" if reason == "not_present" else "illegible")
        results.append(
            ExtractedField(
                field=raw.get("field", "unknown"),
                value=value,
                confidence=confidence,
                refused=refused,
                status=status,
                source_line=raw.get("source_line"),
            )
        )
    return results


def agent_chat(raw_markdown: str, extracted_fields: list[dict], findings: list[dict], totals: dict, messages: list[dict]) -> str:
    """Prompt Sarvam-30B to act as an agent that asks for missing info, with full document context."""
    client = get_client()
    
    missing_fields = [f.get("field") for f in extracted_fields if f.get("refused") or f.get("value") is None]
    
    system_prompt = f"""You are a helpful health-insurance claim assistant.
Your goal is to answer the user's questions about their claim and help them complete their claim form by asking for missing information.

--- CONTEXT ---
The following required fields could not be extracted from the uploaded documents and are MISSING:
{', '.join(missing_fields) if missing_fields else 'None. All fields are present.'}

EXTRACTED FIELDS:
{json.dumps(extracted_fields, indent=2)}

AUDIT FINDINGS (Rejection Risks):
{json.dumps(findings, indent=2)}

TOTALS:
{json.dumps(totals, indent=2)}

RAW DOCUMENT TEXT:
{raw_markdown}
---------------

Instructions:
1. If the user asks a question about their claim, answer it based on the EXTRACTED FIELDS, AUDIT FINDINGS, TOTALS, and RAW DOCUMENT TEXT provided above.
2. If there are missing fields, proactively ask the user to provide them one by one. Do NOT ask for all missing fields at once.
3. When the user provides a field, acknowledge it, and then ask for the next missing field.
4. If all fields are present or once all missing fields are collected, tell the user that the form is complete and they are ready to submit.
5. Be concise and polite.
"""
    
    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
        
    response = client.chat.completions(
        model="sarvam-30b",
        messages=api_messages,
        max_tokens=1024,
        reasoning_effort=None,
    )
    return response.choices[0].message.content


def run_pipeline(
    file_path: str, field_specs: list[ClaimFormFieldSpec], language: str = "hi-IN"
) -> ExtractionResult:
    t0 = time.monotonic()
    markdown_text = digitise(file_path, language=language)
    t1 = time.monotonic()
    fields = extract_fields(markdown_text, field_specs)
    t2 = time.monotonic()
    return ExtractionResult(
        fields=fields,
        raw_markdown=markdown_text,
        digitise_seconds=round(t1 - t0, 2),
        extract_seconds=round(t2 - t1, 2),
    )


async def run_pipeline_async(
    file_path: str, field_specs: list[ClaimFormFieldSpec], language: str = "hi-IN"
) -> ExtractionResult:
    return await asyncio.to_thread(run_pipeline, file_path, field_specs, language)


async def run_pipeline_many(
    file_paths: list[str], field_specs: list[ClaimFormFieldSpec], language: str = "hi-IN"
) -> list[ExtractionResult]:
    """Run the digitise->extract pipeline for multiple files concurrently."""
    return await asyncio.gather(*(run_pipeline_async(p, field_specs, language) for p in file_paths))
