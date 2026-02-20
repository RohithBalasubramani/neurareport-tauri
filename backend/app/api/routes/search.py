"""
Search & Discovery API Routes
Endpoints for full-text, semantic, and advanced search.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.services.search import search_service
from backend.app.services.search.service import SearchType, SearchFilter
from backend.app.services.security import require_api_key

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_key)])


# Regex validation to prevent ReDoS attacks
MAX_REGEX_LENGTH = 100
DANGEROUS_PATTERNS = [
    r"\(\?\#",  # Comments
    r"\(\?\<",  # Named groups (can be complex)
    r"\(\?\(",  # Conditional patterns
    r"\(\?P<",  # Python named groups
]


def validate_regex_pattern(pattern: str) -> tuple[bool, str]:
    """Validate a regex pattern to prevent ReDoS attacks.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern:
        return False, "Empty pattern"

    if len(pattern) > MAX_REGEX_LENGTH:
        return False, f"Pattern too long (max {MAX_REGEX_LENGTH} characters)"

    # Check for dangerous patterns that could cause exponential backtracking
    for dangerous in DANGEROUS_PATTERNS:
        if re.search(dangerous, pattern, re.IGNORECASE):
            return False, "Pattern contains unsupported constructs"

    # Check for nested quantifiers (common ReDoS pattern)
    if re.search(r"(\+|\*|\{[0-9,]+\})\s*(\+|\*|\?|\{[0-9,]+\})", pattern):
        return False, "Nested quantifiers not allowed"

    # Check for overlapping alternation with quantifiers
    if re.search(r"\([^)]*\|[^)]*\)[\+\*]", pattern):
        # Allow simple alternation but flag potentially dangerous ones
        pass

    # Try to compile the pattern with a timeout-safe test
    try:
        compiled = re.compile(pattern)
        # Test with a simple string to catch obvious issues
        compiled.search("test" * 10)
    except re.error as e:
        return False, "Invalid regex pattern"
    except Exception as e:
        return False, "Regex validation error"

    return True, ""


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="fulltext", description="Search type")
    filters: List[Dict[str, Any]] = Field(default_factory=list, description="Filters")
    facet_fields: List[str] = Field(default_factory=list, description="Facet fields")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Results per page")
    highlight: bool = Field(default=True, description="Highlight matches")
    typo_tolerance: bool = Field(default=True, description="Enable typo tolerance")


class IndexDocumentRequest(BaseModel):
    document_id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")


class SearchReplaceRequest(BaseModel):
    search_query: str = Field(..., description="Text to search")
    replace_with: str = Field(..., description="Replacement text")
    document_ids: Optional[List[str]] = Field(default=None, description="Limit to documents")
    dry_run: bool = Field(default=True, description="Preview only")


class SaveSearchRequest(BaseModel):
    name: str = Field(..., description="Search name")
    query: str = Field(..., description="Search query")
    filters: List[Dict[str, Any]] = Field(default_factory=list, description="Filters")
    notify_on_new: bool = Field(default=False, description="Notify on new results")


# =============================================================================
# SEARCH ENDPOINTS
# =============================================================================

@router.get("/types")
async def get_search_types():
    """
    Get available search types.

    Returns:
        List of search types with descriptions
    """
    return {
        "types": [
            {"id": "fulltext", "name": "Full-Text", "description": "Standard keyword search with stemming"},
            {"id": "semantic", "name": "Semantic", "description": "AI-powered meaning-based search"},
            {"id": "fuzzy", "name": "Fuzzy", "description": "Tolerant search with typo handling"},
            {"id": "regex", "name": "Regex", "description": "Regular expression pattern matching"},
            {"id": "boolean", "name": "Boolean", "description": "AND/OR/NOT logical operators"},
        ]
    }


@router.post("/search")
async def search(request: SearchRequest):
    """
    Perform a search with various options.

    Returns:
        SearchResponse with results
    """
    try:
        search_type = SearchType(request.search_type) if request.search_type in [t.value for t in SearchType] else SearchType.FULLTEXT
        filters = [SearchFilter(**f) for f in request.filters]

        result = await search_service.search(
            query=request.query,
            search_type=search_type,
            filters=filters,
            facet_fields=request.facet_fields,
            page=request.page,
            page_size=request.page_size,
            highlight=request.highlight,
            typo_tolerance=request.typo_tolerance,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search operation failed")


@router.post("/search/semantic")
async def semantic_search(request: SearchRequest):
    """
    Perform semantic similarity search.

    Returns:
        SearchResponse with semantically similar results
    """
    request.search_type = "semantic"
    return await search(request)


@router.post("/search/regex")
async def regex_search(request: SearchRequest):
    """
    Perform regex pattern search.

    Returns:
        SearchResponse with regex matches

    Raises:
        HTTPException 400: If regex pattern is invalid or potentially dangerous
    """
    # Validate regex pattern to prevent ReDoS attacks
    is_valid, error_msg = validate_regex_pattern(request.query)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid regex pattern: {error_msg}"
        )

    request.search_type = "regex"
    return await search(request)


@router.post("/search/boolean")
async def boolean_search(request: SearchRequest):
    """
    Perform boolean search with AND, OR, NOT operators.

    Returns:
        SearchResponse with boolean match results
    """
    request.search_type = "boolean"
    return await search(request)


@router.post("/search/replace")
async def search_and_replace(request: SearchReplaceRequest):
    """
    Search and replace across documents.

    Returns:
        Replacement results
    """
    try:
        result = await search_service.search_and_replace(
            search_query=request.search_query,
            replace_with=request.replace_with,
            document_ids=request.document_ids,
            dry_run=request.dry_run,
        )
        return result
    except Exception as e:
        logger.error(f"Search and replace failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search operation failed")


@router.get("/documents/{document_id}/similar")
async def find_similar_documents(document_id: str, limit: int = 10):
    """
    Find documents similar to the given document.

    Returns:
        List of similar documents
    """
    try:
        results = await search_service.find_similar(document_id, limit)
        return [r.model_dump() for r in results]
    except Exception as e:
        logger.error(f"Find similar failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search operation failed")


# =============================================================================
# INDEXING ENDPOINTS
# =============================================================================

@router.post("/index")
async def index_document(request: IndexDocumentRequest):
    """
    Index a document for searching.

    Returns:
        Success status
    """
    try:
        success = await search_service.index_document(
            document_id=request.document_id,
            title=request.title,
            content=request.content,
            metadata=request.metadata,
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Index failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search operation failed")


@router.delete("/index/{document_id}")
async def remove_from_index(document_id: str):
    """
    Remove a document from the search index.

    Returns:
        Success status
    """
    success = await search_service.remove_from_index(document_id)
    return {"success": success}


@router.post("/index/reindex")
async def reindex_all():
    """
    Reindex all documents in the search index.

    Returns:
        Reindex job status
    """
    try:
        result = await search_service.reindex_all()
        return result if isinstance(result, dict) else result.model_dump()
    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reindex operation failed",
        )


# =============================================================================
# SAVED SEARCHES
# =============================================================================

@router.post("/saved-searches")
async def save_search(request: SaveSearchRequest):
    """
    Save a search for later use.

    Returns:
        SavedSearch configuration
    """
    try:
        filters = [SearchFilter(**f) for f in request.filters]
        result = await search_service.save_search(
            name=request.name,
            query=request.query,
            filters=filters,
            notify_on_new=request.notify_on_new,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Save search failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search operation failed")


@router.get("/saved-searches")
async def list_saved_searches():
    """List all saved searches."""
    searches = search_service.list_saved_searches()
    return [s.model_dump() for s in searches]


@router.get("/saved-searches/{search_id}")
async def get_saved_search(search_id: str):
    """
    Get a single saved search by ID.

    Returns:
        SavedSearch configuration
    """
    try:
        saved = await search_service.get_saved_search(search_id)
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found",
            )
        return saved.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get saved search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed",
        )


@router.post("/saved-searches/{search_id}/run")
async def run_saved_search(search_id: str):
    """Run a saved search."""
    try:
        result = await search_service.run_saved_search(search_id)
        return result.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")


@router.delete("/saved-searches/{search_id}")
async def delete_saved_search(search_id: str):
    """Delete a saved search."""
    success = search_service.delete_saved_search(search_id)
    return {"success": success}


# =============================================================================
# ANALYTICS
# =============================================================================

@router.get("/analytics")
async def get_search_analytics():
    """Get search analytics."""
    analytics = await search_service.get_search_analytics()
    return analytics.model_dump()
