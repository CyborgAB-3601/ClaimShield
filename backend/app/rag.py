import re

from rank_bm25 import BM25Okapi

CHUNK_CHARS = 900
CHUNK_OVERLAP = 150

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.casefold())


def _page_marker_before(text: str, index: int) -> str | None:
    marker = None
    for m in re.finditer(r"\[PAGE (\d+)\]", text[:index]):
        marker = m.group(1)
    return marker


def chunk_text(text: str, chunk_chars: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[tuple[str | None, str]]:
    """Split paginated source text into overlapping (page, chunk) windows.

    Sliding-window chunking over the whole document (rather than only near literal
    keyword hits) so a clause phrased differently than any fixed keyword list can still
    be found by the BM25 index built over these chunks.
    """
    chunks: list[tuple[str | None, str]] = []
    step = max(chunk_chars - overlap, 1)
    for start in range(0, len(text), step):
        end = start + chunk_chars
        window = text[start:end].strip()
        if not window:
            continue
        page = _page_marker_before(text, start)
        chunks.append((page, window))
        if end >= len(text):
            break
    return chunks


class ChunkIndex:
    """Runtime BM25 index over a single document's chunks — built fresh per request.

    No embeddings API is available in the Sarvam SDK, so retrieval is keyword-ranked
    (BM25) rather than vector similarity. This still gives far better recall than a
    literal-substring keyword scan because BM25 ranks chunks by term overlap/frequency
    across the whole document instead of requiring an exact phrase match.
    """

    def __init__(self, text: str):
        self.chunks = chunk_text(text)
        tokenized = [_tokenize(chunk) for _, chunk in self.chunks]
        self._bm25 = BM25Okapi(tokenized) if tokenized else None

    def query(self, query: str, k: int = 4) -> list[tuple[str | None, str]]:
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        top = [i for i in ranked[:k] if scores[i] > 0]
        return [self.chunks[i] for i in top]
