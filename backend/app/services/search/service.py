"""
Search & Discovery Service
Provides full-text, semantic, fuzzy, and advanced search capabilities.
"""
from __future__ import annotations

import logging
import re
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SearchType(str, Enum):
    """Types of search."""
    FULLTEXT = "fulltext"
    SEMANTIC = "semantic"
    FUZZY = "fuzzy"
    REGEX = "regex"
    BOOLEAN = "boolean"


class SearchFilter(BaseModel):
    """Search filter configuration."""
    field: str
    operator: str = "eq"  # eq, neq, gt, lt, gte, lte, in, contains, startswith
    value: Any


class SearchFacet(BaseModel):
    """Search facet result."""
    field: str
    values: List[Dict[str, Any]] = Field(default_factory=list)  # {value, count}


class SearchHighlight(BaseModel):
    """Search result highlight."""
    field: str
    snippets: List[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Individual search result."""
    document_id: str
    score: float
    title: str
    snippet: Optional[str] = None
    highlights: List[SearchHighlight] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    matched_terms: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    query: str
    total_results: int
    page: int = 1
    page_size: int = 20
    results: List[SearchResult] = Field(default_factory=list)
    facets: List[SearchFacet] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    did_you_mean: Optional[str] = None
    search_time_ms: float = 0


def _utc_now() -> datetime:
    """Return current UTC time (avoids deprecated utcnow)."""
    return datetime.now(timezone.utc)


class SavedSearch(BaseModel):
    """Saved search configuration."""
    search_id: str
    name: str
    query: str
    filters: List[SearchFilter] = Field(default_factory=list)
    notify_on_new: bool = False
    created_at: datetime = Field(default_factory=_utc_now)
    last_run: Optional[datetime] = None
    result_count: int = 0


class SearchAnalytics(BaseModel):
    """Search analytics data."""
    total_searches: int = 0
    unique_queries: int = 0
    no_results_queries: List[str] = Field(default_factory=list)
    popular_queries: List[Dict[str, Any]] = Field(default_factory=list)
    trending_queries: List[str] = Field(default_factory=list)


class SearchService:
    """
    Comprehensive search service with multiple search types,
    faceted search, saved searches, and analytics.
    """

    def __init__(self):
        import threading
        self._lock = threading.Lock()
        self._index: Dict[str, Dict[str, Any]] = {}  # document_id -> document data
        self._inverted_index: Dict[str, Set[str]] = {}  # term -> document_ids
        self._saved_searches: Dict[str, SavedSearch] = {}
        self._search_history: List[Dict[str, Any]] = []
        self._embeddings_cache: Dict[str, List[float]] = {}

    async def index_document(
        self,
        document_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Index a document for searching.

        Args:
            document_id: Unique document ID
            title: Document title
            content: Document content
            metadata: Additional metadata

        Returns:
            True if indexed successfully
        """
        with self._lock:
            # Store document
            self._index[document_id] = {
                "id": document_id,
                "title": title,
                "content": content,
                "metadata": metadata or {},
                "indexed_at": datetime.now(timezone.utc).isoformat(),
            }

            # Build inverted index
            terms = self._tokenize(f"{title} {content}")
            for term in terms:
                if term not in self._inverted_index:
                    self._inverted_index[term] = set()
                self._inverted_index[term].add(document_id)

        return True

    async def remove_from_index(self, document_id: str) -> bool:
        """Remove a document from the search index."""
        with self._lock:
            if document_id not in self._index:
                return False

            # Remove from inverted index
            doc = self._index[document_id]
            terms = self._tokenize(f"{doc['title']} {doc['content']}")
            for term in terms:
                if term in self._inverted_index:
                    self._inverted_index[term].discard(document_id)
                    if not self._inverted_index[term]:
                        del self._inverted_index[term]

            del self._index[document_id]
        return True

    async def search(
        self,
        query: str,
        search_type: SearchType = SearchType.FULLTEXT,
        filters: Optional[List[SearchFilter]] = None,
        facet_fields: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20,
        highlight: bool = True,
        typo_tolerance: bool = True,
    ) -> SearchResponse:
        """
        Perform a search with various options.

        Args:
            query: Search query
            search_type: Type of search to perform
            filters: Filters to apply
            facet_fields: Fields to generate facets for
            page: Page number
            page_size: Results per page
            highlight: Whether to highlight matches
            typo_tolerance: Enable fuzzy matching for typos

        Returns:
            SearchResponse with results
        """
        start_time = datetime.now(timezone.utc)

        # Get matching documents based on search type
        if search_type == SearchType.SEMANTIC:
            matches = await self._semantic_search(query)
        elif search_type == SearchType.FUZZY:
            matches = await self._fuzzy_search(query, typo_tolerance)
        elif search_type == SearchType.REGEX:
            matches = await self._regex_search(query)
        elif search_type == SearchType.BOOLEAN:
            matches = await self._boolean_search(query)
        else:
            matches = await self._fulltext_search(query, typo_tolerance)

        # Apply filters
        if filters:
            matches = self._apply_filters(matches, filters)

        # Sort by score
        matches.sort(key=lambda x: x[1], reverse=True)

        # Pagination
        total = len(matches)
        self._track_search(query, results=total)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_matches = matches[start_idx:end_idx]

        # Build results
        results = []
        for doc_id, score in page_matches:
            doc = self._index.get(doc_id)
            if not doc:
                continue

            highlights = []
            if highlight:
                highlights = self._generate_highlights(doc, query)

            snippet = self._generate_snippet(doc["content"], query)

            results.append(SearchResult(
                document_id=doc_id,
                score=score,
                title=doc["title"],
                snippet=snippet,
                highlights=highlights,
                metadata=doc.get("metadata", {}),
                matched_terms=self._get_matched_terms(doc, query),
            ))

        # Generate facets
        facets = []
        if facet_fields:
            facets = self._generate_facets([m[0] for m in matches], facet_fields)

        # Get suggestions
        suggestions = await self._get_suggestions(query)

        # Check for "did you mean"
        did_you_mean = None
        if total == 0 and typo_tolerance:
            did_you_mean = await self._get_spelling_suggestion(query)

        elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        return SearchResponse(
            query=query,
            total_results=total,
            page=page,
            page_size=page_size,
            results=results,
            facets=facets,
            suggestions=suggestions,
            did_you_mean=did_you_mean,
            search_time_ms=elapsed_ms,
        )

    async def search_and_replace(
        self,
        search_query: str,
        replace_with: str,
        document_ids: Optional[List[str]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Search and replace across multiple documents.

        Args:
            search_query: Text to search for
            replace_with: Replacement text
            document_ids: Limit to specific documents
            dry_run: If True, only show what would be replaced

        Returns:
            Dict with replacement details
        """
        results = {
            "search_query": search_query,
            "replace_with": replace_with,
            "dry_run": dry_run,
            "documents_affected": 0,
            "total_replacements": 0,
            "changes": [],
        }

        target_docs = document_ids or list(self._index.keys())

        for doc_id in target_docs:
            doc = self._index.get(doc_id)
            if not doc:
                continue

            # Find occurrences
            content = doc["content"]
            occurrences = len(re.findall(re.escape(search_query), content, re.IGNORECASE))

            if occurrences > 0:
                results["documents_affected"] += 1
                results["total_replacements"] += occurrences

                if not dry_run:
                    # Perform replacement
                    new_content = re.sub(
                        re.escape(search_query),
                        replace_with,
                        content,
                        flags=re.IGNORECASE
                    )
                    doc["content"] = new_content
                    # Re-index
                    await self.index_document(
                        doc_id, doc["title"], new_content, doc.get("metadata")
                    )

                results["changes"].append({
                    "document_id": doc_id,
                    "title": doc["title"],
                    "occurrences": occurrences,
                })

        return results

    async def find_similar(
        self,
        document_id: str,
        limit: int = 10,
    ) -> List[SearchResult]:
        """
        Find documents similar to the given document.

        Args:
            document_id: Source document ID
            limit: Maximum results

        Returns:
            List of similar documents
        """
        doc = self._index.get(document_id)
        if not doc:
            return []

        # Use document content as query for semantic similarity
        query = f"{doc['title']} {doc['content'][:500]}"
        matches = await self._semantic_search(query)

        # Remove the source document
        matches = [(id, score) for id, score in matches if id != document_id]
        matches = matches[:limit]

        results = []
        for doc_id, score in matches:
            sim_doc = self._index.get(doc_id)
            if sim_doc:
                results.append(SearchResult(
                    document_id=doc_id,
                    score=score,
                    title=sim_doc["title"],
                    snippet=sim_doc["content"][:200],
                    metadata=sim_doc.get("metadata", {}),
                ))

        return results

    async def save_search(
        self,
        name: str,
        query: str,
        filters: Optional[List[SearchFilter]] = None,
        notify_on_new: bool = False,
    ) -> SavedSearch:
        """
        Save a search for later use.

        Args:
            name: Search name
            query: Search query
            filters: Filters to apply
            notify_on_new: Notify when new results are found

        Returns:
            SavedSearch configuration
        """
        search_id = hashlib.sha256(f"{name}:{query}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]

        saved = SavedSearch(
            search_id=search_id,
            name=name,
            query=query,
            filters=filters or [],
            notify_on_new=notify_on_new,
        )

        self._saved_searches[search_id] = saved
        return saved

    async def run_saved_search(self, search_id: str) -> SearchResponse:
        """Run a saved search."""
        if search_id not in self._saved_searches:
            raise ValueError(f"Saved search {search_id} not found")

        saved = self._saved_searches[search_id]
        result = await self.search(
            query=saved.query,
            filters=saved.filters,
        )

        # Update saved search
        saved.last_run = datetime.now(timezone.utc)
        saved.result_count = result.total_results

        return result

    def list_saved_searches(self) -> List[SavedSearch]:
        """List all saved searches."""
        return list(self._saved_searches.values())

    def delete_saved_search(self, search_id: str) -> bool:
        """Delete a saved search."""
        if search_id in self._saved_searches:
            del self._saved_searches[search_id]
            return True
        return False

    async def get_search_analytics(self) -> SearchAnalytics:
        """Get search analytics."""
        if not self._search_history:
            return SearchAnalytics()

        # Calculate analytics
        queries = [h["query"] for h in self._search_history]
        unique_queries = list(set(queries))

        # Find no-results queries
        no_results = [h["query"] for h in self._search_history if h.get("results", 0) == 0]

        # Popular queries
        query_counts = {}
        for q in queries:
            query_counts[q] = query_counts.get(q, 0) + 1

        popular = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        popular_queries = [{"query": q, "count": c} for q, c in popular]

        # Trending (recent unique queries)
        recent_queries = [h["query"] for h in self._search_history[-50:]]
        trending = list(dict.fromkeys(recent_queries))[:10]

        return SearchAnalytics(
            total_searches=len(self._search_history),
            unique_queries=len(unique_queries),
            no_results_queries=list(set(no_results))[:20],
            popular_queries=popular_queries,
            trending_queries=trending,
        )

    # ==========================================================================
    # PRIVATE METHODS
    # ==========================================================================

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms."""
        # Lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r"\b\w+\b", text)
        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                      "have", "has", "had", "do", "does", "did", "will", "would", "could",
                      "should", "may", "might", "must", "shall", "can", "of", "to", "in",
                      "for", "on", "with", "at", "by", "from", "as", "or", "and", "not"}
        return [t for t in tokens if t not in stop_words and len(t) > 1]

    async def _fulltext_search(
        self,
        query: str,
        typo_tolerance: bool,
    ) -> List[Tuple[str, float]]:
        """Perform full-text search."""
        terms = self._tokenize(query)
        if not terms:
            return []

        # Find documents containing any term
        doc_scores: Dict[str, float] = {}

        for term in terms:
            matching_terms = [term]

            # Add fuzzy matches if typo tolerance enabled
            if typo_tolerance:
                matching_terms.extend(self._get_fuzzy_terms(term))

            for match_term in matching_terms:
                if match_term in self._inverted_index:
                    for doc_id in self._inverted_index[match_term]:
                        # TF-IDF-like scoring
                        doc = self._index.get(doc_id)
                        if doc:
                            tf = doc["content"].lower().count(match_term)
                            idf = len(self._index) / (len(self._inverted_index.get(match_term, set())) + 1)
                            score = tf * idf
                            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + score

        return list(doc_scores.items())

    async def _semantic_search(self, query: str) -> List[Tuple[str, float]]:
        """Perform semantic similarity search."""
        # Get query embedding
        query_embedding = await self._get_embedding(query)
        if not query_embedding:
            # Fall back to full-text search
            return await self._fulltext_search(query, True)

        # Calculate similarity with all documents
        results = []
        for doc_id, doc in self._index.items():
            doc_embedding = await self._get_embedding(doc["content"][:1000])
            if doc_embedding:
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                results.append((doc_id, similarity))

        return results

    async def _fuzzy_search(
        self,
        query: str,
        typo_tolerance: bool,
    ) -> List[Tuple[str, float]]:
        """Perform fuzzy search with edit distance."""
        return await self._fulltext_search(query, typo_tolerance=True)

    async def _regex_search(self, pattern: str) -> List[Tuple[str, float]]:
        """Perform regex search."""
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return []

        results = []
        for doc_id, doc in self._index.items():
            matches = regex.findall(doc["content"])
            if matches:
                results.append((doc_id, len(matches)))

        return results

    async def _boolean_search(self, query: str) -> List[Tuple[str, float]]:
        """Perform boolean search with AND, OR, NOT operators."""
        # Parse boolean query
        # Simple implementation: split by AND/OR/NOT
        query = query.upper()

        # Handle NOT
        excluded_terms = set()
        if " NOT " in query:
            parts = query.split(" NOT ")
            query = parts[0]
            for part in parts[1:]:
                excluded_terms.update(self._tokenize(part))

        # Handle OR
        or_groups = query.split(" OR ")

        all_matches = set()
        for group in or_groups:
            # Handle AND within group
            and_terms = self._tokenize(group)
            if not and_terms:
                continue

            # Find docs with all AND terms
            group_docs = None
            for term in and_terms:
                term_docs = self._inverted_index.get(term.lower(), set())
                if group_docs is None:
                    group_docs = term_docs.copy()
                else:
                    group_docs &= term_docs

            if group_docs:
                all_matches |= group_docs

        # Exclude NOT terms
        for term in excluded_terms:
            excluded_docs = self._inverted_index.get(term.lower(), set())
            all_matches -= excluded_docs

        return [(doc_id, 1.0) for doc_id in all_matches]

    def _get_fuzzy_terms(self, term: str, max_distance: int = 1) -> List[str]:
        """Get similar terms within edit distance."""
        fuzzy_matches = []
        for indexed_term in self._inverted_index.keys():
            if self._edit_distance(term, indexed_term) <= max_distance:
                fuzzy_matches.append(indexed_term)
        return fuzzy_matches

    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance."""
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return len(s1)

        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]

    def _apply_filters(
        self,
        matches: List[Tuple[str, float]],
        filters: List[SearchFilter],
    ) -> List[Tuple[str, float]]:
        """Apply filters to search results."""
        filtered = []
        for doc_id, score in matches:
            doc = self._index.get(doc_id)
            if not doc:
                continue

            passes_filters = True
            for f in filters:
                value = doc.get("metadata", {}).get(f.field) or doc.get(f.field)

                if value is None:
                    passes_filters = False
                elif f.operator == "eq":
                    passes_filters = value == f.value
                elif f.operator == "neq":
                    passes_filters = value != f.value
                elif f.operator == "gt":
                    passes_filters = value > f.value
                elif f.operator == "lt":
                    passes_filters = value < f.value
                elif f.operator == "gte":
                    passes_filters = value >= f.value
                elif f.operator == "lte":
                    passes_filters = value <= f.value
                elif f.operator == "in":
                    passes_filters = value in f.value
                elif f.operator == "contains":
                    passes_filters = f.value in str(value)
                elif f.operator == "startswith":
                    passes_filters = str(value).startswith(f.value)

                if not passes_filters:
                    break

            if passes_filters:
                filtered.append((doc_id, score))

        return filtered

    def _generate_highlights(
        self,
        doc: Dict[str, Any],
        query: str,
    ) -> List[SearchHighlight]:
        """Generate highlighted snippets."""
        highlights = []
        terms = self._tokenize(query)

        for field in ["title", "content"]:
            text = doc.get(field, "")
            snippets = []

            for term in terms:
                pattern = re.compile(f"(.{{0,50}}){re.escape(term)}(.{{0,50}})", re.IGNORECASE)
                for match in pattern.finditer(text):
                    snippet = f"...{match.group(1)}<mark>{term}</mark>{match.group(2)}..."
                    snippets.append(snippet)

            if snippets:
                highlights.append(SearchHighlight(field=field, snippets=snippets[:3]))

        return highlights

    def _generate_snippet(self, content: str, query: str, length: int = 200) -> str:
        """Generate a snippet around the first match."""
        terms = self._tokenize(query)
        if not terms:
            return content[:length]

        # Find first occurrence
        for term in terms:
            idx = content.lower().find(term.lower())
            if idx >= 0:
                start = max(0, idx - 50)
                end = min(len(content), idx + length)
                snippet = content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                return snippet

        return content[:length]

    def _get_matched_terms(self, doc: Dict[str, Any], query: str) -> List[str]:
        """Get terms from query that matched in document."""
        terms = self._tokenize(query)
        content_lower = doc["content"].lower()
        return [t for t in terms if t in content_lower]

    def _generate_facets(
        self,
        doc_ids: List[str],
        fields: List[str],
    ) -> List[SearchFacet]:
        """Generate facets for the given fields."""
        facets = []

        for field in fields:
            value_counts: Dict[Any, int] = {}

            for doc_id in doc_ids:
                doc = self._index.get(doc_id)
                if not doc:
                    continue

                value = doc.get("metadata", {}).get(field) or doc.get(field)
                if value:
                    if isinstance(value, list):
                        for v in value:
                            value_counts[v] = value_counts.get(v, 0) + 1
                    else:
                        value_counts[value] = value_counts.get(value, 0) + 1

            values = [{"value": v, "count": c} for v, c in sorted(value_counts.items(), key=lambda x: x[1], reverse=True)]
            facets.append(SearchFacet(field=field, values=values[:20]))

        return facets

    async def _get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions based on query."""
        terms = self._tokenize(query)
        if not terms:
            return []

        # Find terms that start with the last term
        last_term = terms[-1]
        suggestions = set()

        for term in self._inverted_index.keys():
            if term.startswith(last_term) and term != last_term:
                suggestions.add(term)
                if len(suggestions) >= 5:
                    break

        return list(suggestions)

    async def _get_spelling_suggestion(self, query: str) -> Optional[str]:
        """Get spelling correction suggestion."""
        terms = self._tokenize(query)
        corrected_terms = []

        for term in terms:
            if term in self._inverted_index:
                corrected_terms.append(term)
            else:
                # Find closest match
                best_match = None
                best_distance = 3

                for indexed_term in self._inverted_index.keys():
                    dist = self._edit_distance(term, indexed_term)
                    if dist < best_distance:
                        best_distance = dist
                        best_match = indexed_term

                corrected_terms.append(best_match or term)

        corrected = " ".join(corrected_terms)
        return corrected if corrected != query.lower() else None

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using the embedding pipeline."""
        cache_key = hashlib.md5(text[:1000].encode()).hexdigest()
        if cache_key in self._embeddings_cache:
            return self._embeddings_cache[cache_key]

        try:
            from backend.app.services.vectorstore.embedding_pipeline import EmbeddingPipeline

            pipeline = EmbeddingPipeline()
            embedding = await pipeline.embed_query(text[:8000])
            self._embeddings_cache[cache_key] = embedding
            return embedding

        except Exception as e:
            logger.warning(f"Failed to get embedding: {e}")
            return None

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _track_search(self, query: str, results: int = 0):
        """Track search for analytics."""
        with self._lock:
            self._search_history.append({
                "query": query,
                "results": results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            # Keep only last 1000 searches
            if len(self._search_history) > 1000:
                self._search_history = self._search_history[-1000:]


# Singleton instance
search_service = SearchService()
