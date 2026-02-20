"""Design API Routes.

REST API endpoints for brand kits and themes.
"""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from backend.app.api.middleware import limiter, RATE_LIMIT_STRICT

from backend.app.schemas.design.brand_kit import (
    AccessibleColorsRequest,
    AccessibleColorsResponse,
    ApplyBrandKitRequest,
    AssetResponse,
    BrandKitCreate,
    BrandKitExport,
    BrandKitResponse,
    BrandKitUpdate,
    ColorContrastRequest,
    ColorContrastResponse,
    ColorPaletteRequest,
    ColorPaletteResponse,
    FontInfo,
    FontPairingsResponse,
    ThemeCreate,
    ThemeResponse,
    ThemeUpdate,
)
from backend.app.services.design.service import design_service
from backend.app.services.security import require_api_key

logger = logging.getLogger("neura.api.design")

router = APIRouter(tags=["design"], dependencies=[Depends(require_api_key)])


def _handle_design_error(exc: Exception, operation: str) -> HTTPException:
    """Map design service errors to HTTP status codes."""
    logger.error("%s failed: %s", operation, exc, exc_info=True)
    return HTTPException(
        status_code=500,
        detail=f"{operation} failed due to an internal error.",
    )


# Brand Kit endpoints


@router.post("/brand-kits", response_model=BrandKitResponse)
async def create_brand_kit(request: BrandKitCreate):
    """Create a new brand kit."""
    try:
        return await design_service.create_brand_kit(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Brand kit creation") from exc


@router.get("/brand-kits", response_model=list[BrandKitResponse])
async def list_brand_kits(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all brand kits."""
    try:
        all_kits = await design_service.list_brand_kits()
        return all_kits[offset:offset + limit]
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Brand kit listing") from exc


@router.get("/brand-kits/{kit_id}", response_model=BrandKitResponse)
async def get_brand_kit(kit_id: str):
    """Get a brand kit by ID."""
    try:
        kit = await design_service.get_brand_kit(kit_id)
        if not kit:
            raise HTTPException(status_code=404, detail="Brand kit not found")
        return kit
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Brand kit retrieval") from exc


@router.put("/brand-kits/{kit_id}", response_model=BrandKitResponse)
async def update_brand_kit(kit_id: str, request: BrandKitUpdate):
    """Update a brand kit."""
    try:
        kit = await design_service.update_brand_kit(kit_id, request)
        if not kit:
            raise HTTPException(status_code=404, detail="Brand kit not found")
        return kit
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Brand kit update") from exc


@router.delete("/brand-kits/{kit_id}")
async def delete_brand_kit(kit_id: str):
    """Delete a brand kit."""
    try:
        deleted = await design_service.delete_brand_kit(kit_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Brand kit not found")
        return {"status": "deleted", "id": kit_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Brand kit deletion") from exc


@router.post("/brand-kits/{kit_id}/set-default", response_model=BrandKitResponse)
async def set_default_brand_kit(kit_id: str):
    """Set a brand kit as the default."""
    try:
        kit = await design_service.set_default_brand_kit(kit_id)
        if not kit:
            raise HTTPException(status_code=404, detail="Brand kit not found")
        return kit
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Set default brand kit") from exc


@router.post("/brand-kits/{kit_id}/apply")
async def apply_brand_kit(kit_id: str, request: ApplyBrandKitRequest):
    """Apply brand kit to a document."""
    try:
        result = await design_service.apply_brand_kit(
            kit_id=kit_id,
            document_id=request.document_id,
            elements=request.elements,
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Apply brand kit") from exc


# Color palette endpoints


@router.post("/color-palette", response_model=ColorPaletteResponse)
@limiter.limit(RATE_LIMIT_STRICT)
async def generate_color_palette(request: Request, req: ColorPaletteRequest):
    """Generate a color palette based on color harmony."""
    try:
        result = await asyncio.to_thread(
            design_service.generate_color_palette,
            base_color=req.base_color,
            harmony_type=req.harmony_type,
            count=req.count,
        )
        return JSONResponse(content=result.model_dump() if hasattr(result, 'model_dump') else result)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Color palette generation") from exc


# Theme endpoints


@router.post("/themes", response_model=ThemeResponse)
async def create_theme(request: ThemeCreate):
    """Create a new theme."""
    try:
        return await design_service.create_theme(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Theme creation") from exc


@router.get("/themes", response_model=list[ThemeResponse])
async def list_themes(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all themes."""
    try:
        all_themes = await design_service.list_themes()
        return all_themes[offset:offset + limit]
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Theme listing") from exc


@router.get("/themes/{theme_id}", response_model=ThemeResponse)
async def get_theme(theme_id: str):
    """Get a theme by ID."""
    try:
        theme = await design_service.get_theme(theme_id)
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        return theme
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Theme retrieval") from exc


@router.put("/themes/{theme_id}", response_model=ThemeResponse)
async def update_theme(theme_id: str, request: ThemeUpdate):
    """Update a theme."""
    try:
        theme = await design_service.update_theme(theme_id, request)
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        return theme
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Theme update") from exc


@router.delete("/themes/{theme_id}")
async def delete_theme(theme_id: str):
    """Delete a theme."""
    try:
        deleted = await design_service.delete_theme(theme_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Theme not found")
        return {"status": "deleted", "id": theme_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Theme deletion") from exc


@router.post("/themes/{theme_id}/activate", response_model=ThemeResponse)
async def activate_theme(theme_id: str):
    """Set a theme as the active theme."""
    try:
        theme = await design_service.set_active_theme(theme_id)
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        return theme
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Theme activation") from exc


# Color utility endpoints


@router.post("/colors/contrast", response_model=ColorContrastResponse)
@limiter.limit(RATE_LIMIT_STRICT)
async def get_color_contrast(request: Request, req: ColorContrastRequest):
    """Compute WCAG contrast ratio between two colors."""
    try:
        result = await asyncio.to_thread(
            design_service.get_color_contrast,
            color1=req.color1,
            color2=req.color2,
        )
        return JSONResponse(content=result.model_dump() if hasattr(result, 'model_dump') else result)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Color contrast check") from exc


@router.post("/colors/accessible", response_model=AccessibleColorsResponse)
@limiter.limit(RATE_LIMIT_STRICT)
async def suggest_accessible_colors(request: Request, req: AccessibleColorsRequest):
    """Suggest accessible text colors for a given background."""
    try:
        result = await asyncio.to_thread(
            design_service.suggest_accessible_colors,
            background_color=req.background_color,
        )
        return JSONResponse(content=result.model_dump() if hasattr(result, 'model_dump') else result)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Accessible color suggestion") from exc


# Typography endpoints


@router.get("/fonts", response_model=list[FontInfo])
async def list_fonts():
    """List available fonts."""
    try:
        return await asyncio.to_thread(design_service.list_fonts)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Font listing") from exc


@router.get("/fonts/pairings", response_model=FontPairingsResponse)
async def get_font_pairings(primary: str = Query(..., description="Primary font name")):
    """Get font pairing suggestions for a primary font."""
    try:
        return await asyncio.to_thread(
            design_service.get_font_pairings,
            primary_font=primary,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Font pairing suggestion") from exc


# Asset endpoints


@router.post("/assets/logo", response_model=AssetResponse)
async def upload_logo(
    file: UploadFile = File(...),
    brand_kit_id: str = Form(...),
):
    """Upload a logo asset for a brand kit."""
    try:
        MAX_LOGO_SIZE = 5 * 1024 * 1024  # 5MB
        content = await file.read()
        if len(content) > MAX_LOGO_SIZE:
            raise HTTPException(status_code=413, detail="Logo file too large (max 5MB)")
        return await design_service.upload_logo(
            filename=file.filename or "logo",
            content=content,
            brand_kit_id=brand_kit_id,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Logo upload") from exc


@router.get("/brand-kits/{kit_id}/assets", response_model=list[AssetResponse])
async def list_assets(kit_id: str):
    """List assets for a brand kit."""
    try:
        return await design_service.list_assets(kit_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Asset listing") from exc


@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete a design asset."""
    try:
        deleted = await design_service.delete_asset(asset_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {"status": "deleted", "id": asset_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Asset deletion") from exc


# Import / Export endpoints


@router.get("/brand-kits/{kit_id}/export", response_model=BrandKitExport)
async def export_brand_kit(kit_id: str, format: str = Query("json")):
    """Export a brand kit."""
    try:
        result = await design_service.export_brand_kit(kit_id, fmt=format)
        if not result:
            raise HTTPException(status_code=404, detail="Brand kit not found")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Brand kit export") from exc


@router.post("/brand-kits/import", response_model=BrandKitResponse)
async def import_brand_kit(data: dict):
    """Import a brand kit from exported data."""
    try:
        return await design_service.import_brand_kit(data)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_design_error(exc, "Brand kit import") from exc


@router.get("/brand-kits/{kit_id}/css")
async def get_brand_kit_css(kit_id: str):
    """Return the injectable CSS block for a brand kit.

    Useful for live previews — inject this ``<style>`` into an iframe to
    see how a template looks with the brand kit applied.
    """
    css = design_service.generate_brand_css_from_id(kit_id)
    if css is None:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return JSONResponse(content={"css": css})


@router.get("/brand-kits/default/css")
async def get_default_brand_kit_css():
    """Return CSS for the default brand kit (if one is set)."""
    # Ensure kits are loaded from state
    await design_service.list_brand_kits()
    css = design_service.get_default_brand_css()
    if css is None:
        return JSONResponse(content={"css": None})
    return JSONResponse(content={"css": css})
