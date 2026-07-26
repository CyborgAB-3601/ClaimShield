import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.merge import merge_fields
from app.rules_engine import load_policy, run_audit
from app.sarvam_client import run_pipeline, run_pipeline_many
from app.schema import AuditResponse, DocumentResult, ExtractionResult

app = FastAPI(title="ClaimShield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
            return run_pipeline(tmp.name)
        except Exception as exc:  # surfaced to the demo UI; M5 hardens this path
            raise HTTPException(status_code=502, detail=f"Extraction pipeline failed: {exc}")


@app.post("/api/audit", response_model=AuditResponse)
async def audit(files: list[UploadFile] = File(...), policy_id: str = Form(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    try:
        policy = load_policy(policy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    tmp_paths: list[str] = []
    filenames: list[str] = []
    tmp_files = []
    try:
        for file in files:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail=f"Empty file upload: {file.filename}")
            suffix = Path(file.filename or "upload").suffix or ".jpg"
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.write(contents)
            tmp.flush()
            tmp.close()
            tmp_files.append(tmp)
            tmp_paths.append(tmp.name)
            filenames.append(file.filename or "upload")

        try:
            results = await run_pipeline_many(tmp_paths)
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

        merged = merge_fields(per_doc_fields)
        findings, totals = run_audit(merged, policy)

        return AuditResponse(
            documents=documents,
            merged_fields=merged,
            policy_id=policy["policy_id"],
            policy_display_name=policy["display_name"],
            findings=findings,
            totals=totals,
        )
    finally:
        for tmp in tmp_files:
            Path(tmp.name).unlink(missing_ok=True)
