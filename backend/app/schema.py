from pydantic import BaseModel


CLAIM_FIELDS = [
    "patient_name",
    "hospital_name",
    "admit_date",
    "discharge_date",
    "diagnosis",
    "procedure",
    "room_category",
    "room_rent_per_day",
    "bill_total",
]


class ExtractedField(BaseModel):
    field: str
    value: str | None
    confidence: float | None
    refused: bool
    source_line: str | None = None


class ExtractionResult(BaseModel):
    fields: list[ExtractedField]
    raw_markdown: str
    digitise_seconds: float
    extract_seconds: float
