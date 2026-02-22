"""Knowledge Management Service.

Document library and knowledge management service.
"""
from __future__ import annotations

import copy
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from backend.app.schemas.knowledge.library import (
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
    DocumentType,
    FAQItem,
    FAQResponse,
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    KnowledgeGraphResponse,
    LibraryDocumentCreate,
    LibraryDocumentResponse,
    LibraryDocumentUpdate,
    RelatedDocumentsResponse,
    SearchResponse,
    SearchResult,
    TagCreate,
    TagResponse,
)

logger = logging.getLogger(__name__)


def _now() -> str:
    """Return current UTC time as ISO 8601 string, matching store.py._now_iso()."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class KnowledgeService:
    """Service for managing document library and knowledge base."""

    def __init__(self):
        self._documents: dict[str, dict] = {}
        self._collections: dict[str, dict] = {}
        self._tags: dict[str, dict] = {}
        self._favorites: set[str] = set()

    async def add_document(
        self,
        request: LibraryDocumentCreate,
    ) -> LibraryDocumentResponse:
        """Add a document to the library."""
        self._load_library()
        doc_id = str(uuid.uuid4())
        now = _now()

        # Determine file size if file path provided
        file_size = None
        if request.file_path:
            try:
                file_size = Path(request.file_path).stat().st_size
            except Exception:
                pass

        doc = {
            "id": doc_id,
            "title": request.title,
            "description": request.description,
            "file_path": request.file_path,
            "file_url": request.file_url,
            "document_type": request.document_type.value,
            "file_size": file_size,
            "tags": request.tags,
            "collections": request.collections,
            "metadata": request.metadata,
            "created_at": now,
            "updated_at": now,
            "last_accessed_at": None,
            "is_favorite": False,
        }

        self._documents[doc_id] = doc

        # Add to collections
        for coll_id in request.collections:
            if coll_id in self._collections:
                self._collections[coll_id]["document_ids"].append(doc_id)

        # Persist
        self._persist_library()

        return self._to_document_response(doc)

    async def get_document(self, doc_id: str) -> Optional[LibraryDocumentResponse]:
        """Get a document by ID."""
        self._load_library()
        doc = self._documents.get(doc_id)
        if not doc:
            return None

        # Update last accessed
        doc["last_accessed_at"] = _now()
        self._persist_library()
        return self._to_document_response(doc)

    async def list_documents(
        self,
        collection_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        document_type: Optional[DocumentType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[LibraryDocumentResponse], int]:
        """List documents with optional filtering."""
        self._load_library()

        docs = list(self._documents.values())

        # Filter by collection
        if collection_id:
            coll = self._collections.get(collection_id)
            if coll:
                doc_ids = set(coll.get("document_ids", []))
                docs = [d for d in docs if d["id"] in doc_ids]

        # Filter by tags
        if tags:
            tag_set = set(tags)
            docs = [d for d in docs if tag_set.intersection(d.get("tags", []))]

        # Filter by document type
        if document_type:
            docs = [d for d in docs if d.get("document_type") == document_type.value]

        # Sort by updated_at
        docs.sort(key=lambda d: d.get("updated_at", ""), reverse=True)

        total = len(docs)
        docs = docs[offset:offset + limit]

        return [self._to_document_response(d) for d in docs], total

    async def update_document(
        self,
        doc_id: str,
        request: LibraryDocumentUpdate,
    ) -> Optional[LibraryDocumentResponse]:
        """Update a document."""
        self._load_library()
        doc = self._documents.get(doc_id)
        if not doc:
            return None

        if request.title is not None:
            doc["title"] = request.title
        if request.description is not None:
            doc["description"] = request.description
        if request.tags is not None:
            doc["tags"] = request.tags
        if request.collections is not None:
            # Update collection memberships
            old_colls = set(doc.get("collections", []))
            new_colls = set(request.collections)

            for coll_id in old_colls - new_colls:
                if coll_id in self._collections:
                    self._collections[coll_id]["document_ids"] = [
                        d for d in self._collections[coll_id]["document_ids"]
                        if d != doc_id
                    ]

            for coll_id in new_colls - old_colls:
                if coll_id in self._collections:
                    self._collections[coll_id]["document_ids"].append(doc_id)

            doc["collections"] = request.collections

        if request.metadata is not None:
            doc["metadata"].update(request.metadata)

        doc["updated_at"] = _now()

        self._persist_library()

        return self._to_document_response(doc)

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        self._load_library()
        if doc_id not in self._documents:
            return False

        doc = self._documents[doc_id]

        # Remove from collections
        for coll_id in doc.get("collections", []):
            if coll_id in self._collections:
                self._collections[coll_id]["document_ids"] = [
                    d for d in self._collections[coll_id]["document_ids"]
                    if d != doc_id
                ]

        del self._documents[doc_id]
        self._favorites.discard(doc_id)

        self._persist_library()

        return True

    async def toggle_favorite(self, doc_id: str) -> bool:
        """Toggle favorite status for a document."""
        self._load_library()
        if doc_id not in self._documents:
            return False

        doc = self._documents[doc_id]
        doc["is_favorite"] = not doc.get("is_favorite", False)

        if doc["is_favorite"]:
            self._favorites.add(doc_id)
        else:
            self._favorites.discard(doc_id)

        self._persist_library()

        return doc["is_favorite"]

    # Collection methods

    async def create_collection(
        self,
        request: CollectionCreate,
    ) -> CollectionResponse:
        """Create a new collection."""
        self._load_library()
        coll_id = str(uuid.uuid4())
        now = _now()

        coll = {
            "id": coll_id,
            "name": request.name,
            "description": request.description,
            "document_ids": request.document_ids,
            "is_smart": request.is_smart,
            "smart_filter": request.smart_filter,
            "icon": request.icon,
            "color": request.color,
            "created_at": now,
            "updated_at": now,
        }

        self._collections[coll_id] = coll
        self._persist_library()

        return self._to_collection_response(coll)

    async def get_collection(self, coll_id: str) -> Optional[CollectionResponse]:
        """Get a collection by ID."""
        self._load_library()
        coll = self._collections.get(coll_id)
        if not coll:
            return None
        return self._to_collection_response(coll)

    async def list_collections(self) -> list[CollectionResponse]:
        """List all collections."""
        self._load_library()
        colls = list(self._collections.values())
        colls.sort(key=lambda c: c.get("name", ""))
        return [self._to_collection_response(c) for c in colls]

    async def update_collection(
        self,
        coll_id: str,
        request: CollectionUpdate,
    ) -> Optional[CollectionResponse]:
        """Update a collection."""
        self._load_library()
        coll = self._collections.get(coll_id)
        if not coll:
            return None

        for field in ["name", "description", "document_ids", "is_smart",
                      "smart_filter", "icon", "color"]:
            value = getattr(request, field, None)
            if value is not None:
                coll[field] = value

        coll["updated_at"] = _now()
        self._persist_library()

        return self._to_collection_response(coll)

    async def delete_collection(self, coll_id: str) -> bool:
        """Delete a collection."""
        self._load_library()
        if coll_id not in self._collections:
            return False

        # Remove collection from documents
        for doc in self._documents.values():
            if coll_id in doc.get("collections", []):
                doc["collections"] = [c for c in doc["collections"] if c != coll_id]

        del self._collections[coll_id]
        self._persist_library()

        return True

    # Tag methods

    async def create_tag(self, request: TagCreate) -> TagResponse:
        """Create a new tag."""
        self._load_library()
        tag_id = str(uuid.uuid4())
        now = _now()

        tag = {
            "id": tag_id,
            "name": request.name,
            "color": request.color,
            "description": request.description,
            "created_at": now,
        }

        self._tags[tag_id] = tag
        self._persist_library()

        return self._to_tag_response(tag)

    async def list_tags(self) -> list[TagResponse]:
        """List all tags."""
        self._load_library()
        tags = list(self._tags.values())
        tags.sort(key=lambda t: t.get("name", ""))
        return [self._to_tag_response(t) for t in tags]

    async def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag."""
        self._load_library()
        tag = self._tags.get(tag_id)
        if not tag:
            return False

        tag_name = tag["name"]

        # Remove tag from documents
        for doc in self._documents.values():
            if tag_name in doc.get("tags", []):
                doc["tags"] = [t for t in doc["tags"] if t != tag_name]

        del self._tags[tag_id]
        self._persist_library()

        return True

    # Collection-document association methods

    async def add_document_to_collection(self, collection_id: str, document_id: str) -> bool:
        """Add a document to a collection."""
        self._load_library()
        coll = self._collections.get(collection_id)
        doc = self._documents.get(document_id)
        if not coll or not doc:
            return False

        doc_ids = coll.setdefault("document_ids", [])
        if document_id not in doc_ids:
            doc_ids.append(document_id)

        colls = doc.setdefault("collections", [])
        if collection_id not in colls:
            colls.append(collection_id)

        now = _now()
        coll["updated_at"] = now
        doc["updated_at"] = now
        self._persist_library()
        return True

    async def remove_document_from_collection(self, collection_id: str, document_id: str) -> bool:
        """Remove a document from a collection."""
        self._load_library()
        coll = self._collections.get(collection_id)
        doc = self._documents.get(document_id)
        if not coll or not doc:
            return False

        coll["document_ids"] = [d for d in coll.get("document_ids", []) if d != document_id]
        doc["collections"] = [c for c in doc.get("collections", []) if c != collection_id]

        now = _now()
        coll["updated_at"] = now
        doc["updated_at"] = now
        self._persist_library()
        return True

    # Document-tag association methods

    async def add_tag_to_document(self, document_id: str, tag_id: str) -> bool:
        """Add a tag to a document by tag ID."""
        self._load_library()
        doc = self._documents.get(document_id)
        tag = self._tags.get(tag_id)
        if not doc or not tag:
            return False

        tag_name = str(tag.get("name") or "").strip()
        if not tag_name:
            return False

        doc_tags = doc.setdefault("tags", [])
        if tag_name not in doc_tags:
            doc_tags.append(tag_name)
            doc["updated_at"] = _now()
            self._persist_library()
        return True

    async def remove_tag_from_document(self, document_id: str, tag_id: str) -> bool:
        """Remove a tag from a document by tag ID."""
        self._load_library()
        doc = self._documents.get(document_id)
        tag = self._tags.get(tag_id)
        if not doc or not tag:
            return False

        tag_name = str(tag.get("name") or "").strip()
        if not tag_name:
            return False

        doc["tags"] = [t for t in doc.get("tags", []) if t != tag_name]
        doc["updated_at"] = _now()
        self._persist_library()
        return True

    async def get_document_activity(self, doc_id: str) -> Optional[list[dict[str, Any]]]:
        """Return a lightweight activity stream for a document."""
        self._load_library()
        doc = self._documents.get(doc_id)
        if not doc:
            return None

        activity: list[dict[str, Any]] = []
        metadata_activity = doc.get("activity")
        if isinstance(metadata_activity, list):
            for entry in metadata_activity:
                if isinstance(entry, dict):
                    activity.append(copy.deepcopy(entry))

        if not activity:
            created_at = doc.get("created_at")
            updated_at = doc.get("updated_at")
            last_accessed_at = doc.get("last_accessed_at")
            if created_at:
                activity.append({"event": "created", "timestamp": created_at, "document_id": doc_id})
            if updated_at and updated_at != created_at:
                activity.append({"event": "updated", "timestamp": updated_at, "document_id": doc_id})
            if last_accessed_at:
                activity.append({"event": "accessed", "timestamp": last_accessed_at, "document_id": doc_id})

        return activity

    async def get_stats(self) -> dict[str, Any]:
        """Return aggregate library metrics."""
        self._load_library()
        docs = list(self._documents.values())
        colls = list(self._collections.values())
        tags = list(self._tags.values())

        document_types: dict[str, int] = {}
        storage_used_bytes = 0
        favorites = 0

        for doc in docs:
            kind = str(doc.get("document_type") or "other")
            document_types[kind] = document_types.get(kind, 0) + 1
            file_size = doc.get("file_size")
            if isinstance(file_size, int) and file_size > 0:
                storage_used_bytes += file_size
            if bool(doc.get("is_favorite")):
                favorites += 1

        return {
            "total_documents": len(docs),
            "total_collections": len(colls),
            "total_tags": len(tags),
            "total_favorites": favorites,
            "storage_used_bytes": storage_used_bytes,
            "document_types": document_types,
        }

    # Search methods

    async def search(
        self,
        query: str,
        document_types: list[DocumentType] = None,
        tags: list[str] = None,
        collections: list[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> SearchResponse:
        """Full-text search across documents."""
        start_time = time.time()
        self._load_library()

        query_lower = query.lower()
        results = []

        for doc in self._documents.values():
            # Simple text matching
            score = 0
            highlights = []

            title = str(doc.get("title") or "").lower()
            description = str(doc.get("description") or "").lower()
            content = str(doc.get("content") or "").lower()

            if query_lower in title:
                score += 2.0
                highlights.append(f"Title: {doc['title']}")
            if query_lower in description:
                score += 1.0
                highlights.append("Description match")
            if query_lower in content:
                score += 1.5
                highlights.append("Content match")

            # Filter by document type
            if document_types:
                if doc.get("document_type") not in [dt.value for dt in document_types]:
                    continue

            # Filter by tags
            if tags:
                if not set(tags).intersection(doc.get("tags", [])):
                    continue

            # Filter by collections
            if collections:
                if not set(collections).intersection(doc.get("collections", [])):
                    continue

            if score > 0:
                results.append({
                    "document": doc,
                    "score": score,
                    "highlights": highlights,
                })

        # Sort by score
        results.sort(key=lambda r: r["score"], reverse=True)
        total = len(results)
        results = results[offset:offset + limit]

        took_ms = (time.time() - start_time) * 1000

        return SearchResponse(
            results=[
                SearchResult(
                    document=self._to_document_response(r["document"]),
                    score=r["score"],
                    highlights=r["highlights"],
                )
                for r in results
            ],
            total=total,
            query=query,
            took_ms=took_ms,
        )

    async def semantic_search(
        self,
        query: str,
        document_ids: list[str] = None,
        top_k: int = 10,
        threshold: float = 0.5,
    ) -> SearchResponse:
        """Semantic search using embeddings (placeholder)."""
        # This would use embeddings for semantic similarity
        # For now, falls back to keyword search
        return await self.search(
            query=query,
            limit=top_k,
        )

    async def auto_tag(
        self,
        doc_id: str,
        max_tags: int = 5,
    ) -> dict:
        """Auto-suggest tags for a document."""
        self._load_library()
        doc = self._documents.get(doc_id)
        if not doc:
            return {"document_id": doc_id, "suggested_tags": [], "confidence_scores": {}}

        # Simple keyword extraction (would use NLP in production)
        text = f"{doc.get('title', '')} {doc.get('description', '')}"
        words = text.lower().split()

        # Count word frequencies
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_counts[word] = word_counts.get(word, 0) + 1

        # Get top words as suggested tags
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        suggested = []
        scores = {}

        for word, count in sorted_words[:max_tags]:
            suggested.append(word)
            scores[word] = min(count / 10, 1.0)  # Normalize score

        return {
            "document_id": doc_id,
            "suggested_tags": suggested,
            "confidence_scores": scores,
        }

    async def find_related(
        self,
        doc_id: str,
        limit: int = 10,
    ) -> RelatedDocumentsResponse:
        """Find documents related to a given document."""
        self._load_library()
        doc = self._documents.get(doc_id)
        if not doc:
            return RelatedDocumentsResponse(document_id=doc_id, related=[])

        # Find documents with overlapping tags
        doc_tags = set(doc.get("tags", []))
        results = []

        for other_doc in self._documents.values():
            if other_doc["id"] == doc_id:
                continue

            other_tags = set(other_doc.get("tags", []))
            overlap = len(doc_tags.intersection(other_tags))

            if overlap > 0:
                score = overlap / max(len(doc_tags), 1)
                results.append({
                    "document": other_doc,
                    "score": score,
                    "highlights": [f"Shared tags: {', '.join(doc_tags.intersection(other_tags))}"],
                })

        results.sort(key=lambda r: r["score"], reverse=True)
        results = results[:limit]

        return RelatedDocumentsResponse(
            document_id=doc_id,
            related=[
                SearchResult(
                    document=self._to_document_response(r["document"]),
                    score=r["score"],
                    highlights=r["highlights"],
                )
                for r in results
            ],
        )

    async def build_knowledge_graph(
        self,
        document_ids: list[str] = None,
        depth: int = 2,
    ) -> KnowledgeGraphResponse:
        """Build a knowledge graph from documents."""
        self._load_library()

        nodes = []
        edges = []

        # Get documents
        docs = list(self._documents.values())
        if document_ids:
            docs = [d for d in docs if d["id"] in document_ids]

        # Add document nodes
        for doc in docs:
            nodes.append(KnowledgeGraphNode(
                id=doc["id"],
                type="document",
                label=doc["title"],
                properties={"type": doc.get("document_type"), "tags": doc.get("tags", [])},
            ))

            # Add tag nodes and edges
            for tag in doc.get("tags", []):
                tag_id = f"tag_{tag}"
                if not any(n.id == tag_id for n in nodes):
                    nodes.append(KnowledgeGraphNode(
                        id=tag_id,
                        type="tag",
                        label=tag,
                        properties={},
                    ))

                edges.append(KnowledgeGraphEdge(
                    source=doc["id"],
                    target=tag_id,
                    type="has_tag",
                    weight=1.0,
                ))

            # Add collection nodes and edges
            for coll_id in doc.get("collections", []):
                coll = self._collections.get(coll_id)
                if coll:
                    if not any(n.id == coll_id for n in nodes):
                        nodes.append(KnowledgeGraphNode(
                            id=coll_id,
                            type="collection",
                            label=coll["name"],
                            properties={},
                        ))

                    edges.append(KnowledgeGraphEdge(
                        source=doc["id"],
                        target=coll_id,
                        type="in_collection",
                        weight=1.0,
                    ))

        return KnowledgeGraphResponse(
            nodes=nodes,
            edges=edges,
            metadata={"document_count": len(docs), "depth": depth},
        )

    async def generate_faq(
        self,
        document_ids: list[str],
        max_questions: int = 10,
    ) -> FAQResponse:
        """Generate FAQ from documents (placeholder for AI integration)."""
        self._load_library()

        items = []

        for doc_id in document_ids[:max_questions]:
            doc = self._documents.get(doc_id)
            if not doc:
                continue

            # Generate placeholder FAQ items
            items.append(FAQItem(
                question=f"What is {doc['title']} about?",
                answer=doc.get("description") or f"This document covers topics related to {doc['title']}.",
                source_document_id=doc_id,
                confidence=0.8,
                category="General",
            ))

        return FAQResponse(
            items=items,
            source_documents=document_ids,
        )

    def _load_library(self) -> None:
        """Load library data from state store.

        Clears local state first to avoid stale data, then loads from store.
        """
        try:
            from backend.app.repositories.state.store import state_store
            with state_store.transaction() as state:
                library = state.get("library", {})
                # Clear stale data before loading
                self._documents.clear()
                self._collections.clear()
                self._tags.clear()
                self._favorites.clear()
                # Load fresh data from store
                self._documents.update(library.get("documents", {}))
                self._collections.update(library.get("collections", {}))
                self._tags.update(library.get("tags", {}))
                self._favorites.update(
                    doc_id
                    for doc_id, doc in self._documents.items()
                    if bool(doc.get("is_favorite"))
                )
        except Exception as e:
            logger.warning(f"Failed to load library from state: {e}")

    def _persist_library(self) -> None:
        """Persist library data to state store.

        Raises:
            RuntimeError: If persistence fails, so caller knows the operation did not complete.
        """
        try:
            from backend.app.repositories.state.store import state_store
            with state_store.transaction() as state:
                state["library"] = {
                    "documents": copy.deepcopy(self._documents),
                    "collections": copy.deepcopy(self._collections),
                    "tags": copy.deepcopy(self._tags),
                }
        except Exception as e:
            logger.error(f"Failed to persist library to state: {e}")
            raise RuntimeError(f"Library persistence failed: {e}") from e

    def _to_document_response(self, doc: dict) -> LibraryDocumentResponse:
        """Convert document dict to response model."""
        return LibraryDocumentResponse(
            id=doc["id"],
            title=doc["title"],
            description=doc.get("description"),
            file_path=doc.get("file_path"),
            file_url=doc.get("file_url"),
            document_type=DocumentType(doc.get("document_type", "other")),
            file_size=doc.get("file_size"),
            tags=doc.get("tags", []),
            collections=doc.get("collections", []),
            metadata=doc.get("metadata", {}),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            last_accessed_at=doc.get("last_accessed_at"),
            is_favorite=doc.get("is_favorite", False),
        )

    def _to_collection_response(self, coll: dict) -> CollectionResponse:
        """Convert collection dict to response model."""
        return CollectionResponse(
            id=coll["id"],
            name=coll["name"],
            description=coll.get("description"),
            document_ids=coll.get("document_ids", []),
            document_count=len(coll.get("document_ids", [])),
            is_smart=coll.get("is_smart", False),
            smart_filter=coll.get("smart_filter"),
            icon=coll.get("icon"),
            color=coll.get("color"),
            created_at=coll["created_at"],
            updated_at=coll["updated_at"],
        )

    def _to_tag_response(self, tag: dict) -> TagResponse:
        """Convert tag dict to response model."""
        # Count documents with this tag
        tag_name = tag["name"]
        doc_count = sum(
            1 for doc in self._documents.values()
            if tag_name in doc.get("tags", [])
        )

        return TagResponse(
            id=tag["id"],
            name=tag["name"],
            color=tag.get("color"),
            description=tag.get("description"),
            document_count=doc_count,
            created_at=tag["created_at"],
        )


# Singleton instance
knowledge_service = KnowledgeService()
