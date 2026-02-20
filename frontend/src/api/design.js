/**
 * Design API Client
 * Handles brand kits, themes, and design system operations.
 */
import { api } from './client';

function asArray(payload, keys = []) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

// ============================================
// Brand Kits
// ============================================

export async function createBrandKit(data) {
  const response = await api.post('/design/brand-kits', data);
  return response.data;
}

export async function getBrandKit(brandKitId) {
  const response = await api.get(`/design/brand-kits/${brandKitId}`);
  return response.data;
}

export async function listBrandKits({ limit, offset } = {}) {
  const params = {};
  if (limit != null) params.limit = limit;
  if (offset != null) params.offset = offset;
  const response = await api.get('/design/brand-kits', { params });
  return asArray(response.data, ['brand_kits', 'kits', 'items', 'results']);
}

export async function updateBrandKit(brandKitId, data) {
  const response = await api.put(`/design/brand-kits/${brandKitId}`, data);
  return response.data;
}

export async function deleteBrandKit(brandKitId) {
  const response = await api.delete(`/design/brand-kits/${brandKitId}`);
  return response.data;
}

export async function setDefaultBrandKit(brandKitId) {
  const response = await api.post(`/design/brand-kits/${brandKitId}/set-default`);
  return response.data;
}

export async function applyBrandKit(brandKitId, documentId) {
  const response = await api.post(`/design/brand-kits/${brandKitId}/apply`, {
    document_id: documentId,
  });
  return response.data;
}

// ============================================
// Themes
// ============================================

export async function createTheme(data) {
  const response = await api.post('/design/themes', data);
  return response.data;
}

export async function getTheme(themeId) {
  const response = await api.get(`/design/themes/${themeId}`);
  return response.data;
}

export async function listThemes({ limit, offset } = {}) {
  const params = {};
  if (limit != null) params.limit = limit;
  if (offset != null) params.offset = offset;
  const response = await api.get('/design/themes', { params });
  return asArray(response.data, ['themes', 'items', 'results']);
}

export async function updateTheme(themeId, data) {
  const response = await api.put(`/design/themes/${themeId}`, data);
  return response.data;
}

export async function deleteTheme(themeId) {
  const response = await api.delete(`/design/themes/${themeId}`);
  return response.data;
}

export async function setActiveTheme(themeId) {
  const response = await api.post(`/design/themes/${themeId}/activate`);
  return response.data;
}

// ============================================
// Color Palettes
// ============================================

export async function generateColorPalette(baseColor, harmonyType = 'complementary', count = 5) {
  const response = await api.post('/design/color-palette', {
    base_color: baseColor,
    harmony_type: harmonyType, // 'complementary', 'analogous', 'triadic', 'split-complementary', 'tetradic'
    count,
  });
  return response.data;
}

export async function getColorContrast(color1, color2) {
  const response = await api.post('/design/colors/contrast', {
    color1,
    color2,
  });
  return response.data;
}

export async function suggestAccessibleColors(backgroundColor) {
  const response = await api.post('/design/colors/accessible', {
    background_color: backgroundColor,
  });
  return response.data;
}

// ============================================
// Typography
// ============================================

export async function listFonts() {
  const response = await api.get('/design/fonts');
  return asArray(response.data, ['fonts', 'items', 'results']);
}

export async function getFontPairings(primaryFont) {
  const response = await api.get('/design/fonts/pairings', {
    params: { primary: primaryFont },
  });
  return response.data;
}

// ============================================
// Assets
// ============================================

export async function uploadLogo(file, brandKitId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('brand_kit_id', brandKitId);

  const response = await api.post('/design/assets/logo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function listAssets(brandKitId) {
  const response = await api.get(`/design/brand-kits/${brandKitId}/assets`);
  return asArray(response.data, ['assets', 'items', 'results']);
}

export async function deleteAsset(assetId) {
  const response = await api.delete(`/design/assets/${assetId}`);
  return response.data;
}

// ============================================
// Export
// ============================================

export async function exportBrandKit(brandKitId, format = 'json') {
  const response = await api.get(`/design/brand-kits/${brandKitId}/export`, {
    params: { format },
  });
  return response.data;
}

export async function getBrandKitCss(brandKitId) {
  const response = await api.get(`/design/brand-kits/${brandKitId}/css`);
  return response.data;
}

export async function getDefaultBrandKitCss() {
  const response = await api.get('/design/brand-kits/default/css');
  return response.data;
}

export async function importBrandKit(data) {
  const response = await api.post('/design/brand-kits/import', data);
  return response.data;
}
