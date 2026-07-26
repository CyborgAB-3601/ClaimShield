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
    source_document: str | None = None


class ExtractionResult(BaseModel):
    fields: list[ExtractedField]
    raw_markdown: str
    digitise_seconds: float
    extract_seconds: float


class DocumentResult(BaseModel):
    filename: str
    fields: list[ExtractedField]
    raw_markdown: str
    digitise_seconds: float
    extract_seconds: float


class Finding(BaseModel):
    check: str
    risk: str
    verdict: str
    rupee_impact: float | None
    clause_ref: str
    page: int
    quote: str
    source_document: str | None = None
    source_line: str | None = None


class AuditTotals(BaseModel):
    bill_total: float | None
    claimable_amount: float | None
    deductible_amount: float | None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    raw_markdown: str
    messages: list[ChatMessage]
    extracted_fields: list[ExtractedField]
    findings: list[Finding]
    totals: AuditTotals


class ChatResponse(BaseModel):
    reply: str


class AuditResponse(BaseModel):
    documents: list[DocumentResult]
    merged_fields: list[ExtractedField]
    policy_id: str
    policy_display_name: str
    findings: list[Finding]
    totals: AuditTotals
