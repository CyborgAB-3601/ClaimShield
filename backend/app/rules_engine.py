import json
from datetime import datetime
from pathlib import Path

from app.schema import ROOM_RENT_FIELD, AuditTotals, ExtractedField, Finding

DATE_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y"]


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    cleaned = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None

POLICIES_DIR = Path(__file__).parent / "policies"


def load_policy(policy_id: str) -> dict:
    path = POLICIES_DIR / f"{policy_id}.json"
    if not path.exists():
        raise ValueError(f"Unknown policy_id: {policy_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def _field_map(fields: list[ExtractedField]) -> dict[str, ExtractedField]:
    return {f.field: f for f in fields}


def _parse_amount(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.replace("₹", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _resolve(fields: dict[str, ExtractedField], audit_aliases: dict[str, str | None], concept: str) -> ExtractedField | None:
    """Look up a field the audit needs by the concept's dynamically-resolved alias
    (see claim_form_extractor.py) rather than a fixed field name — the claim form may not
    ask for this concept at all, in which case the alias is None and this returns None.
    """
    key = audit_aliases.get(concept)
    return fields.get(key) if key else None


def _check_room_rent(fields: dict[str, ExtractedField], policy: dict) -> Finding:
    rule = policy.get("room_rent")
    rent_field = fields.get(ROOM_RENT_FIELD)
    if rule is None:
        return Finding(
            check="room_rent",
            risk="insufficient_data",
            verdict="No room-rent clause could be verified in the uploaded policy document.",
            rupee_impact=None,
            clause_ref="not found",
            page=None,
            quote="",
            source_document=rent_field.source_document if rent_field else None,
            source_line=rent_field.source_line if rent_field else None,
        )
    if rent_field is None or rent_field.refused or _parse_amount(rent_field.value) is None:
        return Finding(
            check="room_rent",
            risk="insufficient_data",
            verdict="Room rent per day could not be read from the documents — cannot verify against the policy's room-rent terms.",
            rupee_impact=None,
            clause_ref=rule["clause_ref"],
            page=rule["page"],
            quote=rule["quote"],
            source_document=rent_field.source_document if rent_field else None,
            source_line=rent_field.source_line if rent_field else None,
        )

    if rule["rule"] == "at_actuals":
        return Finding(
            check="room_rent",
            risk="none",
            verdict="No room-rent cap in this policy — the full room charge is claimable under this head.",
            rupee_impact=0.0,
            clause_ref=rule["clause_ref"],
            page=rule["page"],
            quote=rule["quote"],
            source_document=rent_field.source_document,
            source_line=rent_field.source_line,
        )

    # Capped-plan variants are not evaluated in M1 (only the base "at_actuals" policy ships).
    return Finding(
        check="room_rent",
        risk="insufficient_data",
        verdict="This policy variant's room-rent cap is not evaluated in the current rule-sheet.",
        rupee_impact=None,
        clause_ref=rule["clause_ref"],
        page=rule["page"],
        quote=rule["quote"],
        source_document=rent_field.source_document,
        source_line=rent_field.source_line,
    )


def _check_waiting_period(
    fields: dict[str, ExtractedField], policy: dict, audit_aliases: dict[str, str | None]
) -> Finding:
    rule = policy.get("waiting_period_initial")
    diagnosis_field = _resolve(fields, audit_aliases, "diagnosis")
    inception_field = _resolve(fields, audit_aliases, "policy_inception_date")
    admit_field = _resolve(fields, audit_aliases, "admit_date")

    if rule is None:
        return Finding(
            check="waiting_period",
            risk="insufficient_data",
            verdict="No waiting-period clause could be verified in the uploaded policy document.",
            rupee_impact=None,
            clause_ref="not found",
            page=None,
            quote="",
            source_document=diagnosis_field.source_document if diagnosis_field else None,
            source_line=diagnosis_field.source_line if diagnosis_field else None,
        )

    inception_date = _parse_date(inception_field.value) if inception_field and not inception_field.refused else None
    admit_date = _parse_date(admit_field.value) if admit_field and not admit_field.refused else None

    if inception_date is not None and admit_date is not None:
        gap_days = (admit_date - inception_date).days
        if gap_days < rule["days"]:
            return Finding(
                check="waiting_period",
                risk="likely_rejection",
                verdict=(
                    f"Admission was {gap_days} day(s) after the policy started — inside the "
                    f"{rule['days']}-day initial waiting period. Likely rejection — verify with insurer/CA."
                ),
                rupee_impact=None,
                clause_ref=rule["clause_ref"],
                page=rule["page"],
                quote=rule["quote"],
                source_document=inception_field.source_document,
                source_line=inception_field.source_line,
            )
        return Finding(
            check="waiting_period",
            risk="none",
            verdict=(
                f"Admission was {gap_days} day(s) after the policy started — outside the "
                f"{rule['days']}-day initial waiting period on this check."
            ),
            rupee_impact=0.0,
            clause_ref=rule["clause_ref"],
            page=rule["page"],
            quote=rule["quote"],
            source_document=inception_field.source_document,
            source_line=inception_field.source_line,
        )

    return Finding(
        check="waiting_period",
        risk="insufficient_data",
        verdict=(
            f"This policy excludes illness treatment within {rule['days']} days of policy start "
            f"({rule['clause_ref'].split(',')[-1].strip()}) — the policy inception date was not provided, "
            "so this cannot be confirmed. Verify with the insurer/CA before submitting."
        ),
        rupee_impact=None,
        clause_ref=rule["clause_ref"],
        page=rule["page"],
        quote=rule["quote"],
        source_document=diagnosis_field.source_document if diagnosis_field else None,
        source_line=diagnosis_field.source_line if diagnosis_field else None,
    )


def _compute_totals(
    fields: dict[str, ExtractedField], room_rent_finding: Finding, audit_aliases: dict[str, str | None]
) -> AuditTotals:
    bill_field = _resolve(fields, audit_aliases, "bill_total")
    bill_total = _parse_amount(bill_field.value) if bill_field and not bill_field.refused else None
    if bill_total is None:
        return AuditTotals(bill_total=None, claimable_amount=None, deductible_amount=None)

    deductible = room_rent_finding.rupee_impact if room_rent_finding.rupee_impact is not None else None
    if deductible is None:
        return AuditTotals(bill_total=bill_total, claimable_amount=None, deductible_amount=None)

    claimable = round(bill_total - deductible, 2)
    return AuditTotals(bill_total=bill_total, claimable_amount=claimable, deductible_amount=deductible)


def run_audit(
    fields: list[ExtractedField], policy: dict, audit_aliases: dict[str, str | None]
) -> tuple[list[Finding], AuditTotals]:
    fmap = _field_map(fields)
    room_rent_finding = _check_room_rent(fmap, policy)
    waiting_period_finding = _check_waiting_period(fmap, policy, audit_aliases)
    totals = _compute_totals(fmap, room_rent_finding, audit_aliases)
    return [room_rent_finding, waiting_period_finding], totals
