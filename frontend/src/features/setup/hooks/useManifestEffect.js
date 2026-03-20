import { useEffect } from 'react'
import { withBase, fetchArtifactManifest } from '@/api/client'

function withCache(src, cacheKey) {
  if (!src) return src
  const key = cacheKey ?? Date.now()
  try {
    const base = typeof window !== 'undefined' ? window.location.origin : 'http://localhost'
    const url = new URL(src, base)
    url.searchParams.set('v', key)
    return url.toString()
  } catch {
    const basePart = src.split('?')[0]
    return `${basePart}?v=${encodeURIComponent(key)}`
  }
}

/**
 * Fetches the artifact manifest when preview.templateId changes
 * and updates htmlUrls + cacheKey accordingly.
 */
export function useManifestEffect({ preview, previewKind, previewUploadsBase, setCacheKey, setHtmlUrls }) {
  useEffect(() => {
    if (!preview?.templateId) return
    let cancelled = false
    ;(async () => {
      try {
        const manifest = await fetchArtifactManifest(preview.templateId, { kind: previewKind })
        if (cancelled) return
        const producedAt = manifest?.produced_at
        const key = producedAt ? Date.parse(producedAt) || producedAt : Date.now()
        setCacheKey(key)
        const files = manifest?.files || {}
        const templateRel = files['template_p1.html'] || 'template_p1.html'
        const llm2Rel = files['template_llm2.html'] || templateRel
        const finalRel = files['report_final.html'] || null
        const templateBase = withBase(`${previewUploadsBase}/${preview.templateId}/${templateRel}`)
        const llm2Base = withBase(`${previewUploadsBase}/${preview.templateId}/${llm2Rel}`)
        const finalBase = finalRel ? withBase(`${previewUploadsBase}/${preview.templateId}/${finalRel}`) : null
        setHtmlUrls(() => ({
          template: withCache(templateBase, key),
          llm2: withCache(llm2Base, key),
          final: finalBase ? withCache(finalBase, key) : null,
        }))
      } catch {
        if (cancelled) return
        const key = Date.now()
        setCacheKey(key)
        setHtmlUrls((prev) => ({
          ...prev,
          template: withCache(withBase(`${previewUploadsBase}/${preview.templateId}/template_p1.html`), key),
          llm2: withCache(withBase(`${previewUploadsBase}/${preview.templateId}/template_llm2.html`), key),
        }))
      }
    })()
    return () => {
      cancelled = true
    }
  }, [preview?.templateId, previewKind, previewUploadsBase, setCacheKey, setHtmlUrls])
}
