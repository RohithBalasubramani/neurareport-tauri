"""Document chunking and indexing with section awareness.

Supports markdown-style section headers so that chunk boundaries
align with logical document structure whenever possible.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger("neura.indexes.document")

# Regex matching markdown headers (# through ###).
_SECTION_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class ChunkingConfig:
    """Controls how documents are split into chunks."""

    chunk_size: int = 512
    chunk_overlap: int = 50
    separator: str = "\n\n"
    respect_sections: bool = True


# ---------------------------------------------------------------------------
# Section-aware chunking
# ---------------------------------------------------------------------------

def section_aware_chunk(
    content: str,
    config: ChunkingConfig,
) -> list[dict]:
    """Split *content* into chunks that respect markdown section boundaries.

    When ``config.respect_sections`` is ``True``, the text is first split
    on markdown headers (``#``, ``##``, ``###``).  Each section is then
    sub-chunked using size-based splitting so no chunk exceeds
    ``config.chunk_size`` characters.

    Returns a list of dicts::

        {"text": "...", "section": "Section Title", "chunk_index": 0}
    """
    if not content or not content.strip():
        return []

    if not config.respect_sections:
        return _size_based_chunk(content, section="", config=config)

    # --- Split on section headers -----------------------------------------
    sections: list[tuple[str, str]] = []  # (title, body)
    header_matches = list(_SECTION_RE.finditer(content))

    if not header_matches:
        # No headers found; treat entire content as one section.
        return _size_based_chunk(content, section="", config=config)

    # Text before the first header.
    preamble = content[: header_matches[0].start()].strip()
    if preamble:
        sections.append(("", preamble))

    for idx, match in enumerate(header_matches):
        title = match.group(2).strip()
        start = match.end()
        end = (
            header_matches[idx + 1].start()
            if idx + 1 < len(header_matches)
            else len(content)
        )
        body = content[start:end].strip()
        if body or title:
            sections.append((title, body))

    # --- Sub-chunk each section -------------------------------------------
    all_chunks: list[dict] = []
    for title, body in sections:
        # Prepend title to body so it appears in the chunk text for context.
        section_text = f"{title}\n{body}" if title else body
        section_chunks = _size_based_chunk(
            section_text, section=title, config=config,
        )
        all_chunks.extend(section_chunks)

    return all_chunks


def _size_based_chunk(
    text: str,
    section: str,
    config: ChunkingConfig,
) -> list[dict]:
    """Split *text* into overlapping chunks of at most *chunk_size* chars."""
    chunks: list[dict] = []
    # First try splitting on the configured separator.
    paragraphs = text.split(config.separator) if config.separator else [text]

    current_chunk: list[str] = []
    current_len = 0
    chunk_index = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If a single paragraph exceeds chunk_size, hard-split it.
        if len(para) > config.chunk_size:
            # Flush any accumulated text first.
            if current_chunk:
                chunks.append({
                    "text": config.separator.join(current_chunk),
                    "section": section,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1
                # Keep overlap from the tail.
                overlap_text = config.separator.join(current_chunk)
                if config.chunk_overlap and len(overlap_text) > config.chunk_overlap:
                    current_chunk = [overlap_text[-config.chunk_overlap:]]
                    current_len = len(current_chunk[0])
                else:
                    current_chunk = []
                    current_len = 0

            # Hard-split the long paragraph.
            for pos in range(0, len(para), config.chunk_size - config.chunk_overlap):
                segment = para[pos: pos + config.chunk_size]
                chunks.append({
                    "text": segment,
                    "section": section,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1
            current_chunk = []
            current_len = 0
            continue

        # Would adding this paragraph exceed the limit?
        sep_len = len(config.separator) if current_chunk else 0
        if current_len + sep_len + len(para) > config.chunk_size and current_chunk:
            chunks.append({
                "text": config.separator.join(current_chunk),
                "section": section,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

            # Overlap: keep tail characters from the last chunk.
            overlap_text = config.separator.join(current_chunk)
            if config.chunk_overlap and len(overlap_text) > config.chunk_overlap:
                current_chunk = [overlap_text[-config.chunk_overlap:]]
                current_len = len(current_chunk[0])
            else:
                current_chunk = []
                current_len = 0

        current_chunk.append(para)
        current_len += sep_len + len(para)

    # Flush remainder.
    if current_chunk:
        chunks.append({
            "text": config.separator.join(current_chunk),
            "section": section,
            "chunk_index": chunk_index,
        })

    return chunks


# ---------------------------------------------------------------------------
# DocumentIndex
# ---------------------------------------------------------------------------

class DocumentIndex:
    """Indexes documents with section-aware chunking.

    Parameters
    ----------
    embedding_pipeline:
        Object exposing ``generate_embeddings(texts)`` and
        ``chunk_text(text, chunk_size, overlap)``.
    vector_store:
        Object exposing ``add(embeddings, texts, metadata_list)``,
        ``search(embedding, top_k)``, and ``delete(filter_dict)``.
    config:
        Optional chunking configuration.  Uses sensible defaults when
        not provided.
    """

    def __init__(
        self,
        embedding_pipeline,
        vector_store,
        config: ChunkingConfig | None = None,
    ) -> None:
        self._embedder = embedding_pipeline
        self._store = vector_store
        self._config = config or ChunkingConfig()

    # -- indexing -----------------------------------------------------------

    def index_document(
        self,
        doc_id: str,
        content: str,
        source: str,
        metadata: dict | None = None,
    ) -> int:
        """Chunk, embed, and store a single document.  Returns chunk count."""
        chunks = section_aware_chunk(content, self._config)
        if not chunks:
            logger.debug("No chunks produced for document %s", doc_id)
            return 0

        texts = [c["text"] for c in chunks]
        embeddings = self._embedder.generate_embeddings(texts)

        base_meta = metadata or {}
        metadata_list = [
            {
                **base_meta,
                "source": source,
                "doc_id": doc_id,
                "section": c["section"],
                "chunk_index": c["chunk_index"],
            }
            for c in chunks
        ]

        self._store.add(embeddings, texts, metadata_list)
        logger.info(
            "Indexed document %s from %s (%d chunks)", doc_id, source, len(chunks),
        )
        return len(chunks)

    def index_documents_batch(self, documents: list[dict]) -> int:
        """Index multiple documents in one call.

        Each element of *documents* must have keys:
        ``doc_id``, ``content``, ``source`` and optionally ``metadata``.

        Returns the total number of chunks indexed.
        """
        total = 0
        for doc in documents:
            count = self.index_document(
                doc_id=doc["doc_id"],
                content=doc["content"],
                source=doc["source"],
                metadata=doc.get("metadata"),
            )
            total += count

        logger.info(
            "Batch-indexed %d documents (%d total chunks)",
            len(documents), total,
        )
        return total

    # -- deletion -----------------------------------------------------------

    def delete_document(self, doc_id: str) -> int:
        """Remove all chunks belonging to *doc_id*.  Returns chunks deleted."""
        try:
            result = self._store.delete({"doc_id": doc_id})
            count = result if isinstance(result, int) else 0
        except Exception:
            logger.exception("Failed to delete chunks for doc_id=%s", doc_id)
            return 0

        logger.info("Deleted %d chunks for document %s", count, doc_id)
        return count

    # -- search -------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        source_filter: str | None = None,
    ) -> list[dict]:
        """Semantic search across indexed documents.

        Parameters
        ----------
        query:
            Natural language search query.
        top_k:
            Maximum number of results to return.
        source_filter:
            If provided, only return results whose ``source`` metadata
            starts with this prefix (e.g. ``"upload:"``,
            ``"knowledge_base:"``).
        """
        query_embedding = self._embedder.generate_embeddings([query])[0]
        # Fetch extra results when filtering so we still return up to top_k.
        fetch_k = top_k * 3 if source_filter else top_k
        results = self._store.search(query_embedding, top_k=fetch_k)

        if source_filter:
            results = [
                r for r in results
                if r.get("metadata", {}).get("source", "").startswith(source_filter)
            ]

        results = results[:top_k]
        logger.debug(
            "Document search returned %d results for: %s",
            len(results), query[:80],
        )
        return results
