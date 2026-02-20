import { withBase } from '../api/client'

export const DEFAULT_PAGE_DIMENSIONS = { width: 794, height: 1123 }

const parseTimestamp = (value) => {
  if (value === null || value === undefined || value === '') return null
  if (typeof value === 'number' && Number.isFinite(value)) return Math.floor(value)
  const numeric = Number(value)
  if (!Number.isNaN(numeric) && Number.isFinite(numeric) && numeric > 0) {
    return Math.floor(numeric)
  }
  const parsed = Date.parse(value)
  if (!Number.isNaN(parsed)) return Math.floor(parsed)
  return String(value)
}

export const appendCacheBuster = (url, ts) => {
  if (!url || ts === null || ts === undefined || ts === '') return url
  const token = parseTimestamp(ts)
  const value = typeof token === 'number' ? token : String(token)
  try {
    const base = typeof window !== 'undefined' ? window.location.origin : 'http://localhost'
    const next = new URL(url, base)
    next.searchParams.set('ts', value)
    return next.toString()
  } catch {
    const sep = url.includes('?') ? '&' : '?'
    return `${url}${sep}ts=${encodeURIComponent(value)}`
  }
}

export const getUploadsBase = (templateOrKind) => {
  const kind =
    typeof templateOrKind === 'string'
      ? templateOrKind
      : templateOrKind?.kind || templateOrKind?.templateKind || templateOrKind?.sourceKind
  return kind === 'excel' ? 'excel-uploads' : 'uploads'
}

const ensureAbsolutePath = (template, path) => {
  if (!path || typeof path !== 'string') return null
  if (/^https?:\/\//i.test(path)) return path
  if (path.startsWith('/')) return path
  const templateId = template?.id || template?.templateId || template?.template_id
  if (!templateId) return path
  const base = getUploadsBase(template)
  return `/${base}/${templateId}/${path}`
}

const pickFirst = (candidates) => candidates.find((item) => typeof item === 'string' && item.length > 0) || null

export function resolveTemplatePreviewUrl(template, options = {}) {
  if (!template) return { url: null, key: null, ts: null }

  const manifest = template.manifest || {}
  const manifestFiles = manifest.files || {}
  const artifacts = template.artifacts || {}
  const templateId = template.id || template.templateId || template.template_id || template?.tplId || null

  const finalCandidates = [
    template.htmlUrls?.final,
    template.final_html_url,
    template.finalHtmlUrl,
    artifacts.final_html_url,
    artifacts.finalHtmlUrl,
    artifacts.final_html,
    manifestFiles['report_final.html'],
  ]

  const templateCandidates = [
    template.htmlUrls?.llm2,
    template.llm2_html_url,
    template.llm2HtmlUrl,
    artifacts.llm2_html_url,
    artifacts.llm2HtmlUrl,
    manifestFiles['template_llm2.html'],
    template.htmlUrls?.template,
    template.template_html_url,
    template.templateHtmlUrl,
    artifacts.template_html_url,
    artifacts.templateHtmlUrl,
    artifacts.template_html,
    manifestFiles['template_p1.html'],
  ]

  const htmlCandidates = [
    template.template_html,
    template.templateHtml,
    template.html_url,
    template.htmlUrl,
    template.llm2_html_url,
    template.llm2HtmlUrl,
    artifacts.html_url,
    artifacts.htmlUrl,
    artifacts.html,
    artifacts.llm2_html_url,
    artifacts.llm2HtmlUrl,
    manifestFiles['template_html'],
    manifestFiles['template_llm2.html'],
    options.fallbackUrl,
  ]

  let raw =
    ensureAbsolutePath(template, pickFirst(finalCandidates)) ||
    ensureAbsolutePath(template, pickFirst(templateCandidates)) ||
    ensureAbsolutePath(template, pickFirst(htmlCandidates))

  if (!raw) return { url: null, key: null, ts: null }

  let resolved = withBase(raw)

  const tsCandidates = [
    options.ts,
    template.previewTs,
    template.preview_ts,
    template.cacheKey,
    template.manifest_produced_at,
    manifest.produced_at,
    template.lastModified,
    template.updated_at,
    template.updatedAt,
    template.created_at,
    template.createdAt,
    template.ts,
  ]
  const tsRaw = tsCandidates.find((value) => value !== undefined && value !== null && value !== '')
  const ts = tsRaw !== undefined ? parseTimestamp(tsRaw) : null

  if (ts !== null) {
    resolved = appendCacheBuster(resolved, ts)
  }

  const keySeed = [templateId || 'preview', ts !== null ? ts : 'na', resolved]
  const key = keySeed.filter(Boolean).join('-')

  return { url: resolved, key, ts }
}

export function resolveTemplateThumbnailUrl(template, options = {}) {
  if (!template) return { url: null }
  const manifest = template.manifest || {}
  const manifestFiles = manifest.files || {}
  const artifacts = template.artifacts || {}

  const candidates = [
    template.thumbnail_url,
    template.thumbnailUrl,
    template.png_url,
    template.pngUrl,
    artifacts.thumbnail_url,
    artifacts.thumbnailUrl,
    artifacts.png_url,
    artifacts.pngUrl,
    artifacts.thumbnail,
    manifestFiles['report_final.png'],
    manifestFiles['thumbnail.png'],
    options.fallbackUrl,
  ]

  const raw = ensureAbsolutePath(template, pickFirst(candidates))
  if (!raw) return { url: null }

  const ts =
    options.ts ||
    template.previewTs ||
    template.cacheKey ||
    manifest.produced_at ||
    template.updated_at ||
    template.updatedAt ||
    template.created_at ||
    template.createdAt
  const withBaseUrl = withBase(raw)
  return { url: appendCacheBuster(withBaseUrl, ts) }
}
