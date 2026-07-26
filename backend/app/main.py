import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.sarvam_client import run_pipeline
from app.schema import ExtractionResult

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
