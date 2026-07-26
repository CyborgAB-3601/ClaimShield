from app.schema import CLAIM_FIELDS, ExtractedField


def merge_fields(per_doc: list[tuple[str, list[ExtractedField]]]) -> list[ExtractedField]:
    """Merge per-document field extractions into one claim record.

    For each CLAIM_FIELDS key, picks the highest-confidence non-refused value
    across all documents. If no document has a usable value, emits a refused
    field so the merged record always has exactly len(CLAIM_FIELDS) entries.
    """
    merged: list[ExtractedField] = []
    for field_name in CLAIM_FIELDS:
        best: ExtractedField | None = None
        best_filename: str | None = None
        for filename, fields in per_doc:
            for f in fields:
                if f.field != field_name or f.refused or f.confidence is None:
                    continue
                if best is None or f.confidence > best.confidence:
                    best = f
                    best_filename = filename
        if best is None:
            merged.append(
                ExtractedField(
                    field=field_name,
                    value=None,
                    confidence=None,
                    refused=True,
                    source_line=None,
                    source_document=None,
                )
            )
        else:
            merged.append(
                ExtractedField(
                    field=field_name,
                    value=best.value,
                    confidence=best.confidence,
                    refused=False,
                    source_line=best.source_line,
                    source_document=best_filename,
                )
            )
    return merged
