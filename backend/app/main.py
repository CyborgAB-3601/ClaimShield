import asyncio
import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.claim_form_extractor import extract_claim_form_schema
from app.doc_text import extract_paginated_text
from app.fill_claim_form import fill_claim_form
from app.merge import merge_fields
from app.policy_extractor import extract_policy_rules
from app.rules_engine import run_audit
from app.sarvam_client import agent_chat, run_pipeline, run_pipeline_many
from app.schema import (
    ROOM_RENT_FIELD,
    AuditResponse,
    ChatRequest,
    ChatResponse,
    ClaimFormFieldSpec,
    DocumentResult,
    ExtractionResult,
)

# Fallback field list for the standalone single-file /api/extract debug endpoint, which
# has no claim form to derive a schema from.
_DEFAULT_EXTRACT_FIELDS = [
    ClaimFormFieldSpec(field_key="patient_name", label="Patient name", section="Debug", hint="Patient's full name."),
    ClaimFormFieldSpec(field_key="hospital_name", label="Hospital name", section="Debug", hint="Treating hospital."),
    ClaimFormFieldSpec(field_key="admit_date", label="Admission date", section="Debug", hint="Date admitted."),
    ClaimFormFieldSpec(field_key="discharge_date", label="Discharge date", section="Debug", hint="Date discharged."),
    ClaimFormFieldSpec(field_key="diagnosis", label="Diagnosis", section="Debug", hint="Primary diagnosis."),
]

# Room rent per day is never a claim-form field (the form only asks for room category),
# but the room-rent-cap audit needs the rate itself, off the itemised bill.
_ROOM_RENT_SPEC = ClaimFormFieldSpec(
    field_key=ROOM_RENT_FIELD,
    label="Room rent per day",
    section="Policy audit (not on claim form)",
    hint="The room charge per day from the itemised bill — needed to check the policy's room-rent cap.",
)

app = FastAPI(title="ClaimShield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/extract", response_model=ExtractionResult)
async def extract(file: UploadFile):
    suffix = Path(file.filename or "upload").suffix or ".jpg"
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file upload")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(contents)
        tmp.flush()
        try:
            return run_pipeline(tmp.name, _DEFAULT_EXTRACT_FIELDS)
        except Exception as exc:  # surfaced to the demo UI; M5 hardens this path
            raise HTTPException(status_code=502, detail=f"Extraction pipeline failed: {exc}")


async def _extract_policy_async(policy_path: str, filename: str) -> dict:
    source_text = await asyncio.to_thread(extract_paginated_text, policy_path)
    return await asyncio.to_thread(extract_policy_rules, source_text, filename)


async def _extract_claim_form_async(form_path: str) -> dict:
    source_text = await asyncio.to_thread(extract_paginated_text, form_path)
    return await asyncio.to_thread(extract_claim_form_schema, source_text)


def _write_temp(contents: bytes, filename: str) -> tempfile._TemporaryFileWrapper:
    suffix = Path(filename or "upload").suffix or ".jpg"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.write(contents)
    tmp.flush()
    tmp.close()
    return tmp


@app.post("/api/audit", response_model=AuditResponse)
async def audit(
    files: list[UploadFile] = File(...),
    policy_file: UploadFile = File(...),
    claim_form: UploadFile = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    tmp_files = []
    try:
        tmp_paths: list[str] = []
        filenames: list[str] = []
        for file in files:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail=f"Empty file upload: {file.filename}")
            tmp = _write_temp(contents, file.filename or "upload")
            tmp_files.append(tmp)
            tmp_paths.append(tmp.name)
            filenames.append(file.filename or "upload")

        policy_contents = await policy_file.read()
        if not policy_contents:
            raise HTTPException(status_code=400, detail="Empty policy file upload")
        policy_tmp = _write_temp(policy_contents, policy_file.filename or "policy")
        tmp_files.append(policy_tmp)

        claim_form_contents = await claim_form.read()
        if not claim_form_contents:
            raise HTTPException(status_code=400, detail="Empty claim form upload")
        claim_form_tmp = _write_temp(claim_form_contents, claim_form.filename or "claim_form")
        tmp_files.append(claim_form_tmp)

        try:
            # The claim-doc field extraction depends on the claim form's own field
            # schema, so it must wait for that; policy-clause extraction is independent
            # and runs concurrently with it instead.
            policy, claim_form_schema = await asyncio.gather(
                _extract_policy_async(policy_tmp.name, policy_file.filename or "policy"),
                _extract_claim_form_async(claim_form_tmp.name),
            )
            field_specs = claim_form_schema["fields"] + [_ROOM_RENT_SPEC]
            audit_aliases = claim_form_schema["audit_aliases"]
            results = await run_pipeline_many(tmp_paths, field_specs)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Extraction pipeline failed: {exc}")

        documents = []
        per_doc_fields = []
        for filename, result in zip(filenames, results):
            for f in result.fields:
                f.source_document = filename
            documents.append(
                DocumentResult(
                    filename=filename,
                    fields=result.fields,
                    raw_markdown=result.raw_markdown,
                    digitise_seconds=result.digitise_seconds,
                    extract_seconds=result.extract_seconds,
                )
            )
            per_doc_fields.append((filename, result.fields))

        merged = merge_fields(per_doc_fields, field_specs)
        findings, totals = run_audit(merged, policy, audit_aliases)

        return AuditResponse(
            documents=documents,
            field_schema=field_specs,
            merged_fields=merged,
            policy_id=policy["policy_id"],
            policy_display_name=policy["display_name"],
            findings=findings,
            totals=totals,
        )
    finally:
        for tmp in tmp_files:
            Path(tmp.name).unlink(missing_ok=True)


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        fields_dict = [f.model_dump() for f in request.extracted_fields]
        findings_dict = [f.model_dump() for f in request.findings]
        totals_dict = request.totals.model_dump()
        reply = agent_chat(request.raw_markdown, fields_dict, findings_dict, totals_dict, messages)
        return ChatResponse(reply=reply)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Chat failed: {exc}")


@app.post("/api/fill-claim-form")
async def fill_claim_form_endpoint(
    claim_form: UploadFile = File(...),
    merged_fields: str = Form(...),
):
    """
    Accept the original blank claim-form PDF and the JSON-serialised list of
    merged ExtractedField objects (from /api/audit), and return the auto-filled
    PDF as a download.

    merged_fields should be the JSON string of AuditResponse.merged_fields.
    """
    pdf_bytes = await claim_form.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Empty claim form PDF")

    try:
        fields_list: list[dict] = json.loads(merged_fields)
    except Exception:
        raise HTTPException(status_code=422, detail="merged_fields must be valid JSON")

    try:
        filled_bytes = fill_claim_form(pdf_bytes, fields_list)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"PDF fill failed: {exc}")

    filename = (claim_form.filename or "claim_form").rsplit(".", 1)[0] + "_filled.pdf"
    return StreamingResponse(
        iter([filled_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
