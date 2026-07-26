from pydantic import BaseModel

# Fixed audit-support field: the claim form only asks for room *category*, never the
# per-day rent, but the room-rent-cap check needs the rate itself (it's on the itemised
# bill, not the form). Kept as a single named exception rather than folding the whole
# audit into claim-form fields — see claim_form_extractor.py.
ROOM_RENT_FIELD = "room_rent_per_day"


class ClaimFormFieldSpec(BaseModel):
    field_key: str
    label: str
    section: str
    hint: str


class ExtractedField(BaseModel):
    field: str
    value: str | None
    confidence: float | None
    refused: bool
    status: str = "filled"  # "filled" | "missing" | "illegible"
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
    page: int | None
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
    field_schema: list[ClaimFormFieldSpec]
    merged_fields: list[ExtractedField]
    policy_id: str
    policy_display_name: str
    findings: list[Finding]
    totals: AuditTotals
