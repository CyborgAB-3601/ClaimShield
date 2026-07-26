from app.schema import ClaimFormFieldSpec, ExtractedField


def merge_fields(
    per_doc: list[tuple[str, list[ExtractedField]]], field_specs: list[ClaimFormFieldSpec]
) -> list[ExtractedField]:
    """Merge per-document field extractions into one claim record.

    field_specs is the dynamic field list derived from the actual uploaded claim form.
    For each field key, picks the highest-confidence non-refused value across all
    documents. If no document has a usable value: emits "illegible" if any document found
    the field but couldn't read it clearly (worth asking the doctor/hospital to redo), or
    "missing" if no document mentions it at all (worth obtaining a different document).
    """
    merged: list[ExtractedField] = []
    for spec in field_specs:
        field_name = spec.field_key
        best: ExtractedField | None = None
        best_filename: str | None = None
        any_illegible = False
        for filename, fields in per_doc:
            for f in fields:
                if f.field != field_name:
                    continue
                if f.refused:
                    if f.status == "illegible":
                        any_illegible = True
                    continue
                if f.confidence is None:
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
                    status="illegible" if any_illegible else "missing",
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
                    status="filled",
                    source_line=best.source_line,
                    source_document=best_filename,
                )
            )
    return merged
