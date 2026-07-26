"""
fill_claim_form.py – Programmatically fill the Star Health reimbursement
                     claim form (Part A, patient-fillable section) with
                     values extracted by the AI pipeline.

Strategy:
  1. Render a transparent reportlab overlay containing only the fill text.
  2. Merge it on top of every page of the original blank PDF via pypdf.
  3. Return the filled bytes so the API can stream them to the browser.

Field-to-coordinate mapping is for the STAR HEALTH "Reimbursement Claim
Form – Part A / Part B" used in this project (A4, 595 × 842 pt).  The
coordinates were derived by calling page.extract_text(visitor_text=…) on
the blank form and measuring where each label ends; the fill value is
placed ~130 pt to the right (or below) the label baseline.

Only the patient-fillable fields are mapped here.  Hospital-only sections
(Part B, hospital declaration) are left untouched.
"""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


# ---------------------------------------------------------------------------
# Coordinate map  – { field_key: (page_index, x, y) }
# page_index is 0-based.  x, y are in PDF user-space points (bottom-left 0,0).
# These values match the STAR HEALTH claim form in this project.
# ---------------------------------------------------------------------------
FIELD_COORDS: dict[str, tuple[int, float, float]] = {
    # ── PAGE 1 : Details of Proposer ──────────────────────────────────────
    "policy_number":          (0, 175.0, 525.0),
    "policy_period":          (0, 370.0, 525.0),
    "proposer_name":          (0, 175.0, 505.0),
    "customer_id":            (0, 395.0, 505.0),
    "employee_name":          (0, 175.0, 490.0),
    "employee_id":            (0, 395.0, 490.0),
    "id_proof_type_proposer": (0, 175.0, 466.0),
    "id_proof_no_proposer":   (0, 370.0, 466.0),
    "ckyc_number":            (0, 175.0, 446.0),
    "pan_card_no":            (0, 370.0, 446.0),
    "address":                (0, 130.0, 426.0),
    "city":                   (0, 395.0, 426.0),
    "email":                  (0, 185.0, 406.0),
    "district":               (0, 395.0, 406.0),
    "mobile_no":              (0, 185.0, 386.0),
    "state":                  (0, 395.0, 386.0),
    "whatsapp_number":        (0, 185.0, 366.0),
    "pin_code":               (0, 395.0, 366.0),

    # ── PAGE 1 : Details of Insured Patient ───────────────────────────────
    "patient_name":           (0, 175.0, 323.0),
    "gender":                 (0, 395.0, 323.0),
    "date_of_birth":          (0, 175.0, 303.0),
    "age":                    (0, 270.0, 303.0),
    "relationship":           (0, 370.0, 303.0),
    "abha_id":                (0, 175.0, 283.0),
    "id_proof_type_patient":  (0, 370.0, 283.0),
    "tpa_id_card_no":         (0, 175.0, 263.0),
    "id_proof_no_patient":    (0, 370.0, 263.0),
    "hospitalisation_due_to": (0, 200.0, 243.0),

    # ── PAGE 2 : Treatment Expenses Claimed ───────────────────────────────
    "hospitalisation_expenses":     (1, 210.0, 771.0),
    "pre_hospitalisation_expenses": (1, 210.0, 753.0),
    "post_hospitalisation_expenses":(1, 445.0, 753.0),
    "ambulance_charges":            (1, 445.0, 771.0),
    "total_claimed":                (1, 210.0, 698.0),

    # Bill details table – first row only (Sl No 1)
    "bill_no_1":     (1, 90.0,  635.0),
    "bill_date_1":   (1, 150.0, 635.0),
    "bill_issuer_1": (1, 250.0, 635.0),
    "bill_detail_1": (1, 350.0, 635.0),
    "bill_amount_1": (1, 500.0, 635.0),

    # Bank details
    "bank_name":        (1, 120.0, 276.0),
    "bank_holder_name": (1, 280.0, 276.0),
    "ifsc_code":        (1, 430.0, 276.0),
    "bank_branch":      (1, 120.0, 256.0),
    "account_number":   (1, 280.0, 249.0),
    "account_type":     (1, 120.0, 249.0),

    # Signature date (page 2 bottom)
    "declaration_date": (1, 70.0, 45.0),
}

# Aliases: canonical field_keys the pipeline produces → form field_keys above.
# Add more as needed when the AI pipeline assigns different keys.
FIELD_ALIASES: dict[str, str] = {
    # patient identity
    "insured_patient_name":      "patient_name",
    "patient_gender":            "gender",
    "patient_dob":               "date_of_birth",
    "date_of_birth_age":         "date_of_birth",
    "dob":                       "date_of_birth",
    "patient_age":               "age",
    "relationship_with_proposer":"relationship",
    # hospitalisation
    "admit_date":                "hospitalisation_due_to",
    "admission_date":            "hospitalisation_due_to",
    "date_of_admission":         "hospitalisation_due_to",
    "diagnosis":                 "hospitalisation_due_to",
    # proposer / policy
    "insurer_name":              "proposer_name",
    "policy_no":                 "policy_number",
    # amounts
    "bill_total":                "total_claimed",
    "hospitalization_expenses":  "hospitalisation_expenses",
    "pre_hospitalization_expenses": "pre_hospitalisation_expenses",
    "post_hospitalization_expenses":"post_hospitalisation_expenses",
}


def _resolve_key(key: str) -> str | None:
    """Return the canonical FIELD_COORDS key for an extracted field key."""
    if key in FIELD_COORDS:
        return key
    return FIELD_ALIASES.get(key)


def _build_overlay(
    filled_values: dict[str, str],
    page_width: float = A4[0],
    page_height: float = A4[1],
) -> PdfReader:
    """
    Return a PdfReader wrapping a 4-page reportlab PDF that contains ONLY
    the filled-in text at the correct coordinates.  All other space is
    transparent so it can be merged on top of the original form.
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Group values by page
    pages: dict[int, list[tuple[float, float, str]]] = {0: [], 1: [], 2: [], 3: []}
    for field_key, value in filled_values.items():
        coord = FIELD_COORDS.get(field_key)
        if coord is None:
            continue
        pg, x, y = coord
        if pg in pages:
            pages[pg].append((x, y, value))

    for pg in range(4):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(0.05, 0.25, 0.65)   # ink-blue, stands out from black labels
        for x, y, value in pages[pg]:
            # Truncate long strings to avoid overflowing into neighbouring columns
            truncated = value[:52] if len(value) > 52 else value
            c.drawString(x, y, truncated)
        c.showPage()

    c.save()
    packet.seek(0)
    return PdfReader(packet)


def fill_claim_form(
    original_pdf_bytes: bytes,
    merged_fields: list[dict[str, Any]],
) -> bytes:
    """
    Fill the claim form PDF with extracted field values.

    Parameters
    ----------
    original_pdf_bytes:
        Raw bytes of the blank CLAIMFORM.pdf.
    merged_fields:
        List of dicts with at least ``field`` and ``value`` keys
        (matches the ExtractedField schema).  Fields with ``refused=True``
        or ``value=None`` are skipped.

    Returns
    -------
    bytes
        The filled PDF, ready to stream to the browser.
    """
    # Build resolved key → value dict (skip refused / empty)
    filled: dict[str, str] = {}
    for f in merged_fields:
        if f.get("refused") or not f.get("value"):
            continue
        key = _resolve_key(f["field"])
        if key:
            filled[key] = str(f["value"]).strip()

    # Read original
    template = PdfReader(io.BytesIO(original_pdf_bytes))
    page0 = template.pages[0]
    # Use actual page dimensions (may differ from A4)
    page_width = float(page0.mediabox.width)
    page_height = float(page0.mediabox.height)

    overlay = _build_overlay(filled, page_width, page_height)

    writer = PdfWriter()
    for i, page in enumerate(template.pages):
        if i < len(overlay.pages):
            page.merge_page(overlay.pages[i])
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()
