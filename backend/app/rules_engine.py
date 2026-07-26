import json
from pathlib import Path

from app.schema import AuditTotals, ExtractedField, Finding

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


def _check_room_rent(fields: dict[str, ExtractedField], policy: dict) -> Finding:
    rule = policy["room_rent"]
    rent_field = fields.get("room_rent_per_day")
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


def _check_waiting_period(fields: dict[str, ExtractedField], policy: dict) -> Finding:
    rule = policy["waiting_period_initial"]
    diagnosis_field = fields.get("diagnosis")
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


def _compute_totals(fields: dict[str, ExtractedField], room_rent_finding: Finding) -> AuditTotals:
    bill_field = fields.get("bill_total")
    bill_total = _parse_amount(bill_field.value) if bill_field and not bill_field.refused else None
    if bill_total is None:
        return AuditTotals(bill_total=None, claimable_amount=None, deductible_amount=None)

    deductible = room_rent_finding.rupee_impact if room_rent_finding.rupee_impact is not None else None
    if deductible is None:
        return AuditTotals(bill_total=bill_total, claimable_amount=None, deductible_amount=None)

    claimable = round(bill_total - deductible, 2)
    return AuditTotals(bill_total=bill_total, claimable_amount=claimable, deductible_amount=deductible)


def run_audit(fields: list[ExtractedField], policy: dict) -> tuple[list[Finding], AuditTotals]:
    fmap = _field_map(fields)
    room_rent_finding = _check_room_rent(fmap, policy)
    waiting_period_finding = _check_waiting_period(fmap, policy)
    totals = _compute_totals(fmap, room_rent_finding)
    return [room_rent_finding, waiting_period_finding], totals
