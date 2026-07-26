import json
import re

from app.rag import ChunkIndex
from app.sarvam_client import _strip_json_fence, get_client

POLICY_EXTRACTION_SYSTEM_PROMPT = """You are extracting structured policy rules from candidate excerpts pulled \
from an Indian health-insurance policy wording document by keyword search. Each excerpt is labelled with the \
clause type it was searched for and may include a "[PAGE N]" marker if the source page is known.

For each of these 3 clause types, look ONLY within its own labelled excerpt section for the matching clause:
1. "room_rent" — the room rent/boarding limit (e.g. "At Actuals", or a cap like a % of sum insured or a fixed \
per-day amount).
2. "proportionate_deduction" — the proportionate-deduction-on-room-rent formula applied when the insured is \
admitted to a room exceeding the eligible category.
3. "waiting_period_initial" — the INITIAL/general waiting period (typically ~30 days from the policy's first \
commencement date, often coded "Excl03"). Do NOT confuse this with the pre-existing-disease (PED) exclusion \
(often "Excl01", typically 36-48 MONTHS, not days) or any other named exclusion — those are different clauses, \
even if they also use the word "waiting period".

Rules (must follow exactly):
1. For each clause type, if its excerpt genuinely contains that clause, copy the relevant sentence(s) EXACTLY \
character-for-character from the excerpt as "quote" — do not paraphrase, summarise, translate, or fix typos. If \
the excerpt doesn't actually contain a clause of that type (e.g. it only matched the search keyword by \
coincidence, or it's actually a different exclusion like PED), set "found" to false and omit "quote".
2. "page" is the number from the "[PAGE N]" marker attached to that excerpt, if any. If none, set "page" to null. \
Never guess a page number.
3. For "waiting_period_initial", the "days" value MUST be a number of DAYS that appears literally within your \
"quote" (e.g. if the quote says "30 days", days=30). If the excerpt's period is stated in months, or no number is \
visible in the quote, set "found" to false.
4. For "room_rent", set "rule" to "at_actuals" if the text says the limit is at actuals / no cap; "capped" if a \
specific cap (percentage or fixed amount) is stated; "other" if unclear.
5. Respond with strict JSON only, in this exact shape:
{"policy_name": "<best-guess policy/plan name from the document, or null>",
 "rules": [
   {"type": "room_rent", "found": <bool>, "quote": "<verbatim or omit>", "clause_ref": "<section label or null>", \
"page": <int or null>, "rule": "<at_actuals|capped|other>"},
   {"type": "proportionate_deduction", "found": <bool>, "quote": "<verbatim or omit>", "clause_ref": "<...>", \
"page": <int or null>},
   {"type": "waiting_period_initial", "found": <bool>, "quote": "<verbatim or omit>", "clause_ref": "<...>", \
"page": <int or null>, "days": <int or null>}
 ]}
"""

CLAUSE_QUERIES = {
    "room_rent": (
        "room rent or boarding, nursing limit per day; room category eligibility; "
        "at actuals or a percentage/fixed cap on the room rent"
    ),
    "proportionate_deduction": (
        "proportionate deduction formula applied to associate medical expenses when the "
        "insured occupies a room exceeding the eligible room rent or category"
    ),
    "waiting_period_initial": (
        "initial waiting period of 30 days from the policy's first commencement date "
        "before illness treatment is covered, Excl03"
    ),
}

RETRIEVAL_K = 4


def _build_candidate_excerpts(index: ChunkIndex) -> str:
    sections = []
    for clause_type, query in CLAUSE_QUERIES.items():
        hits = index.query(query, k=RETRIEVAL_K)
        header = f"=== Candidate excerpts for {clause_type} ==="
        if not hits:
            sections.append(f"{header}\n(no relevant passages retrieved from the document)")
            continue
        body = "\n\n".join(f"[PAGE {page}]\n{excerpt}" if page else excerpt for page, excerpt in hits)
        sections.append(f"{header}\n{body}")
    return "\n\n".join(sections)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _is_grounded(quote: str | None, source_text: str) -> bool:
    if not quote:
        return False
    return _normalize(quote) in _normalize(source_text)


def _days_grounded(days: int | None, quote: str) -> bool:
    if days is None:
        return False
    return str(days) in quote


def extract_policy_rules(markdown_text: str, source_filename: str) -> dict:
    """Ask Sarvam-30B to locate policy clauses within BM25-retrieved candidate excerpts,
    then verify each proposed quote is an actual substring of the full digitised source
    text before trusting it. A clause that isn't grounded (or a numeric detail not
    literally present in its quote) is dropped rather than used — the rules engine
    reports "insufficient data" for it instead.

    Chunking the whole document and retrieving by BM25 relevance to a natural-language
    clause description (rather than handing the model the entire policy, which can run
    50+ pages, or relying on literal keyword substring matches) finds clauses phrased
    differently than any fixed keyword list, while still keeping the request small and
    reducing the chance the model conflates a similar-sounding but different clause (e.g.
    the pre-existing-disease exclusion vs. the initial waiting period).
    """
    index = ChunkIndex(markdown_text)
    candidate_excerpts = _build_candidate_excerpts(index)
    client = get_client()
    response = client.chat.completions(
        model="sarvam-30b",
        messages=[
            {"role": "system", "content": POLICY_EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": candidate_excerpts},
        ],
        max_tokens=3072,
        reasoning_effort=None,
    )
    content = response.choices[0].message.content
    parsed = json.loads(_strip_json_fence(content))

    by_type = {r.get("type"): r for r in parsed.get("rules", [])}

    policy: dict = {
        "policy_id": "runtime",
        "display_name": parsed.get("policy_name") or source_filename,
        "source_document": source_filename,
        "room_rent": None,
        "proportionate_deduction": None,
        "waiting_period_initial": None,
    }

    rr = by_type.get("room_rent")
    if rr and rr.get("found") and _is_grounded(rr.get("quote"), markdown_text):
        policy["room_rent"] = {
            "rule": rr.get("rule") or "other",
            "cap_type": rr.get("rule") or "other",
            "clause_ref": rr.get("clause_ref") or "not stated",
            "page": rr.get("page"),
            "quote": rr["quote"],
        }

    pd = by_type.get("proportionate_deduction")
    if pd and pd.get("found") and _is_grounded(pd.get("quote"), markdown_text):
        policy["proportionate_deduction"] = {
            "clause_ref": pd.get("clause_ref") or "not stated",
            "page": pd.get("page"),
            "quote": pd["quote"],
            "formula": (
                "admissible_amount = billed_amount * "
                "(admissible_room_rent_per_day / actual_room_rent_per_day)"
            ),
        }

    wp = by_type.get("waiting_period_initial")
    if (
        wp
        and wp.get("found")
        and _is_grounded(wp.get("quote"), markdown_text)
        and _days_grounded(wp.get("days"), wp.get("quote", ""))
    ):
        policy["waiting_period_initial"] = {
            "clause_ref": wp.get("clause_ref") or "not stated",
            "page": wp.get("page"),
            "quote": wp["quote"],
            "days": wp["days"],
            "requires_field": "policy_inception_date",
        }

    return policy
