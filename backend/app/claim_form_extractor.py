import json

from app.sarvam_client import _strip_json_fence, get_client
from app.schema import ClaimFormFieldSpec

# Concepts the deterministic rules engine needs to do its ₹ math (room-rent cap,
# waiting-period gap). These are resolved dynamically per claim form below, rather than
# assumed to exist under a fixed field name — a different insurer's form may ask for the
# same fact under a different label, or not ask for it at all.
AUDIT_CONCEPTS = ["admit_date", "diagnosis", "policy_inception_date", "bill_total"]

CLAIM_FORM_SYSTEM_PROMPT = f"""You are reading an Indian health-insurance reimbursement claim form to determine \
which of its fields a claimant could fill in using only two source documents: a hospital discharge summary and \
an itemised hospital bill.

The claim form usually has sections filled by the insured/patient (personal identity, hospitalisation details, \
claimed amounts) and sections filled by someone else entirely (the hospital's own declaration, bank account \
details, PAN, signatures, policy-history/company names, KYC documents). Only the first kind can ever be answered \
from a discharge summary or bill.

Rules (must follow exactly):
1. Include ONLY fields whose value could plausibly appear on a hospital discharge summary or itemised bill: \
patient identity (name, gender, age/DOB), hospitalisation details (hospital name, admission/discharge dates, \
room category, diagnosis, procedure), and claimed treatment amounts.
2. EXCLUDE: anything only the hospital/doctor would fill in on their own declaration section, bank account /
PAN / IFSC / cheque details, insurance policy number / company history / sum insured, KYC identity documents, \
signatures, dates of form submission, and anything about a different claim history entirely.
3. Use the form's own wording for "label" (shorten only if very long). Invent a short lower_snake_case \
"field_key" for each (e.g. "date_of_admission", "room_category_occupied"). "section" should be the form's own \
section heading (e.g. "Section C - Details of insured person hospitalised"). "hint" is one short sentence on \
where in a discharge summary/bill this would be found.
4. Separately, for each of these audit concepts: {", ".join(AUDIT_CONCEPTS)} — decide which field_key from your \
list (if any) semantically represents it. "policy_inception_date" means the date the policy/insurance FIRST \
started (not the claim form's own submission date). "bill_total" means the total treatment/hospitalisation \
expense amount claimed. If no field in your list corresponds, use null.
5. Respond with strict JSON only, in this exact shape:
{{"fields": [{{"field_key": "<name>", "label": "<form label>", "section": "<form section>", \
"hint": "<short guidance>"}}, ...],
 "audit_aliases": {{"admit_date": "<field_key or null>", "diagnosis": "<field_key or null>", \
"policy_inception_date": "<field_key or null>", "bill_total": "<field_key or null>"}}}}
"""


def extract_claim_form_schema(form_text: str) -> dict:
    """Ask Sarvam-30B to read the real uploaded claim form and derive the field list to
    extract, instead of using a fixed hardcoded field list. Returns
    {"fields": [ClaimFormFieldSpec, ...], "audit_aliases": {...}}.
    """
    client = get_client()
    response = client.chat.completions(
        model="sarvam-30b",
        messages=[
            {"role": "system", "content": CLAIM_FORM_SYSTEM_PROMPT},
            {"role": "user", "content": form_text},
        ],
        max_tokens=3072,
        reasoning_effort=None,
    )
    content = response.choices[0].message.content
    parsed = json.loads(_strip_json_fence(content))

    seen_keys: set[str] = set()
    fields: list[ClaimFormFieldSpec] = []
    for raw in parsed.get("fields", []):
        key = raw.get("field_key")
        if not key or key in seen_keys:
            continue
        seen_keys.add(key)
        fields.append(
            ClaimFormFieldSpec(
                field_key=key,
                label=raw.get("label") or key,
                section=raw.get("section") or "Claim form",
                hint=raw.get("hint") or "",
            )
        )

    raw_aliases = parsed.get("audit_aliases") or {}
    audit_aliases = {
        concept: raw_aliases.get(concept) if raw_aliases.get(concept) in seen_keys else None
        for concept in AUDIT_CONCEPTS
    }

    return {"fields": fields, "audit_aliases": audit_aliases}
