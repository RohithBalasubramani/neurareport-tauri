"""
Seed Data Initialization
Provides sample data for new installations to demonstrate features.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
import uuid

logger = logging.getLogger(__name__)


def _now():
    return datetime.now(timezone.utc)


def _days_ago(days: int):
    return _now() - timedelta(days=days)


async def seed_knowledge_library():
    """Seed the knowledge library with sample documents, collections, and tags."""
    from backend.app.services.knowledge.service import knowledge_service
    from backend.app.schemas.knowledge.library import (
        LibraryDocumentCreate,
        CollectionCreate,
        TagCreate,
        DocumentType,
    )

    # Check if already seeded
    docs, total = await knowledge_service.list_documents(limit=1)
    if total > 0:
        logger.info("Knowledge library already has data, skipping seed")
        return

    logger.info("Seeding knowledge library with sample data...")

    # Create tags
    tags = [
        # Tag colors use secondary palette 500 values per Design System v4/v5
        TagCreate(name="Important", color="#F43F5E", description="High priority items"),       # Rose 500
        TagCreate(name="Finance", color="#64748B", description="Financial documents"),         # Slate 500
        TagCreate(name="Marketing", color="#8B5CF6", description="Marketing materials"),       # Violet 500
        TagCreate(name="Technical", color="#06B6D4", description="Technical documentation"),   # Cyan 500
        TagCreate(name="Legal", color="#14B8A6", description="Legal documents"),               # Teal 500
        TagCreate(name="HR", color="#D946EF", description="Human resources"),                  # Fuchsia 500
    ]

    created_tags = []
    for tag in tags:
        created = await knowledge_service.create_tag(tag)
        created_tags.append(created)

    # Create collections
    collections = [
        CollectionCreate(name="Q1 2024 Reports", description="First quarter reports and analysis"),
        CollectionCreate(name="Product Documentation", description="Technical product docs"),
        CollectionCreate(name="Marketing Assets", description="Marketing collateral and campaigns"),
        CollectionCreate(name="Meeting Notes", description="Notes from various meetings"),
    ]

    created_collections = []
    for coll in collections:
        created = await knowledge_service.create_collection(coll)
        created_collections.append(created)

    # Create sample documents
    sample_docs = [
        LibraryDocumentCreate(
            title="Q1 2024 Financial Summary",
            description="Comprehensive financial summary for the first quarter of 2024, including revenue analysis, expense breakdown, and profit margins.",
            document_type=DocumentType.PDF,
            tags=["Finance", "Important"],
            collections=[created_collections[0].id],
            metadata={"author": "Finance Team", "department": "Finance"},
        ),
        LibraryDocumentCreate(
            title="Product Roadmap 2024",
            description="Strategic product roadmap outlining major features, milestones, and release timelines for the year.",
            document_type=DocumentType.PDF,
            tags=["Technical", "Important"],
            collections=[created_collections[1].id],
            metadata={"author": "Product Team", "version": "2.1"},
        ),
        LibraryDocumentCreate(
            title="Marketing Campaign Analysis",
            description="Analysis of Q1 marketing campaigns including social media performance, email metrics, and ROI calculations.",
            document_type=DocumentType.PDF,
            tags=["Marketing"],
            collections=[created_collections[2].id],
            metadata={"campaign": "Spring 2024"},
        ),
        LibraryDocumentCreate(
            title="API Documentation v3.0",
            description="Complete API reference documentation including endpoints, authentication, and code examples.",
            document_type=DocumentType.OTHER,
            tags=["Technical"],
            collections=[created_collections[1].id],
            metadata={"version": "3.0", "format": "API Reference"},
        ),
        LibraryDocumentCreate(
            title="Employee Handbook 2024",
            description="Updated employee handbook with policies, benefits information, and company guidelines.",
            document_type=DocumentType.PDF,
            tags=["HR", "Legal"],
            collections=[],
            metadata={"effective_date": "2024-01-01"},
        ),
        LibraryDocumentCreate(
            title="Board Meeting Notes - January",
            description="Summary notes from the January board meeting covering strategic initiatives and quarterly reviews.",
            document_type=DocumentType.DOCX,
            tags=["Important"],
            collections=[created_collections[3].id],
            metadata={"meeting_date": "2024-01-15"},
        ),
        LibraryDocumentCreate(
            title="Competitor Analysis Report",
            description="Detailed analysis of key competitors including market positioning, strengths, and weaknesses.",
            document_type=DocumentType.PDF,
            tags=["Marketing", "Important"],
            collections=[created_collections[2].id],
            metadata={"analysts": ["Market Research Team"]},
        ),
        LibraryDocumentCreate(
            title="Security Compliance Checklist",
            description="SOC2 and GDPR compliance checklist with current status and remediation items.",
            document_type=DocumentType.XLSX,
            tags=["Technical", "Legal"],
            collections=[created_collections[1].id],
            metadata={"compliance_type": "SOC2, GDPR"},
        ),
    ]

    for doc in sample_docs:
        await knowledge_service.add_document(doc)

    logger.info(f"Seeded {len(sample_docs)} documents, {len(created_collections)} collections, {len(created_tags)} tags")


async def seed_brand_kits():
    """Seed the design system with sample brand kits and themes."""
    from backend.app.services.design.service import design_service
    from backend.app.schemas.design.brand_kit import BrandKitCreate, ThemeCreate

    # Check state store directly first (more reliable than in-memory service)
    try:
        from backend.app.repositories.state.store import state_store
        with state_store.transaction() as state:
            existing = state.get("brand_kits", {})
            if existing and len(existing) > 0:
                logger.info("Brand kits already exist in state store (%d), skipping seed", len(existing))
                return
    except Exception:
        pass

    # Fallback: also check via service
    existing_kits = await design_service.list_brand_kits()
    if len(existing_kits) > 0:
        logger.info("Brand kits already exist, skipping seed")
        return

    logger.info("Seeding brand kits and themes...")

    # Create sample brand kits
    brand_kits = [
        BrandKitCreate(
            name="Corporate Blue",
            primary_color="#1e40af",
            secondary_color="#3b82f6",
            font_family="Inter",
            is_default=True,
        ),
        BrandKitCreate(
            name="Modern Green",
            primary_color="#047857",
            secondary_color="#10b981",
            font_family="Plus Jakarta Sans",
            is_default=False,
        ),
        BrandKitCreate(
            name="Professional Dark",
            primary_color="#1f2937",
            secondary_color="#6b7280",
            font_family="IBM Plex Sans",
            is_default=False,
        ),
    ]

    for kit in brand_kits:
        await design_service.create_brand_kit(kit)

    # Create sample themes
    themes = [
        ThemeCreate(
            name="Light Mode",
            mode="light",
            colors={
                "background": "#ffffff",
                "surface": "#f8fafc",
                "text": "#1e293b",
                "primary": "#3b82f6",
            },
            is_active=True,
        ),
        ThemeCreate(
            name="Dark Mode",
            mode="dark",
            colors={
                "background": "#0f172a",
                "surface": "#1e293b",
                "text": "#f1f5f9",
                "primary": "#60a5fa",
            },
            is_active=False,
        ),
    ]

    for theme in themes:
        await design_service.create_theme(theme)

    logger.info(f"Seeded {len(brand_kits)} brand kits, {len(themes)} themes")


async def seed_connections():
    """Seed sample database connections."""
    from backend.app.repositories.state.store import state_store

    with state_store.transaction() as state:
        connections = state.get("connections", [])

        if len(connections) > 0:
            logger.info("Connections already exist, skipping seed")
            return

    logger.info("Seeding sample connections...")

    sample_connections = [
        {
            "id": str(uuid.uuid4()),
            "name": "Production Analytics DB",
            "db_type": "postgresql",
            "host": "analytics.example.com",
            "port": 5432,
            "database": "analytics",
            "is_active": True,
            "created_at": _now().isoformat(),
            "last_tested": _days_ago(1).isoformat(),
            "status": "connected",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sales Data Warehouse",
            "db_type": "snowflake",
            "host": "org.snowflakecomputing.com",
            "database": "SALES_DW",
            "is_active": True,
            "created_at": _days_ago(30).isoformat(),
            "last_tested": _days_ago(2).isoformat(),
            "status": "connected",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marketing MongoDB",
            "db_type": "mongodb",
            "host": "mongodb.example.com",
            "port": 27017,
            "database": "marketing",
            "is_active": True,
            "created_at": _days_ago(60).isoformat(),
            "last_tested": _days_ago(5).isoformat(),
            "status": "connected",
        },
    ]

    with state_store.transaction() as state:
        state["connections"] = {conn["id"]: conn for conn in sample_connections}

    logger.info(f"Seeded {len(sample_connections)} connections")


async def seed_templates():
    """Seed sample report templates."""
    from backend.app.repositories.state.store import state_store

    with state_store.transaction() as state:
        templates = state.get("templates", [])

        if len(templates) > 0:
            logger.info("Templates already exist, skipping seed")
            return

    logger.info("Seeding sample templates...")

    sample_templates = [
        {
            "id": str(uuid.uuid4()),
            "name": "Monthly Sales Report",
            "description": "Standard monthly sales report with revenue breakdown and trends",
            "category": "Sales",
            "status": "draft",
            "created_at": _days_ago(90).isoformat(),
            "updated_at": _days_ago(5).isoformat(),
            "is_favorite": True,
            "usage_count": 24,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Executive Dashboard",
            "description": "High-level KPI dashboard for executive team review",
            "category": "Executive",
            "status": "draft",
            "created_at": _days_ago(120).isoformat(),
            "updated_at": _days_ago(3).isoformat(),
            "is_favorite": True,
            "usage_count": 48,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Customer Churn Analysis",
            "description": "Customer retention and churn metrics with cohort analysis",
            "category": "Analytics",
            "status": "draft",
            "created_at": _days_ago(45).isoformat(),
            "updated_at": _days_ago(10).isoformat(),
            "is_favorite": False,
            "usage_count": 12,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marketing Campaign ROI",
            "description": "Campaign performance metrics and ROI calculations",
            "category": "Marketing",
            "status": "draft",
            "created_at": _days_ago(30).isoformat(),
            "updated_at": _days_ago(7).isoformat(),
            "is_favorite": False,
            "usage_count": 8,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Inventory Status Report",
            "description": "Current inventory levels, reorder points, and stock alerts",
            "category": "Operations",
            "status": "draft",
            "created_at": _days_ago(60).isoformat(),
            "updated_at": _days_ago(1).isoformat(),
            "is_favorite": False,
            "usage_count": 16,
        },
    ]

    with state_store.transaction() as state:
        state["templates"] = {tpl["id"]: tpl for tpl in sample_templates}

    logger.info(f"Seeded {len(sample_templates)} templates")


async def seed_all():
    """Run all seed functions."""
    logger.info("Starting data seeding...")

    try:
        await seed_knowledge_library()
    except Exception as e:
        logger.warning(f"Failed to seed knowledge library: {e}")

    try:
        await seed_brand_kits()
    except Exception as e:
        logger.warning(f"Failed to seed brand kits: {e}")

    try:
        await seed_connections()
    except Exception as e:
        logger.warning(f"Failed to seed connections: {e}")

    try:
        await seed_templates()
    except Exception as e:
        logger.warning(f"Failed to seed templates: {e}")

    logger.info("Data seeding complete")
