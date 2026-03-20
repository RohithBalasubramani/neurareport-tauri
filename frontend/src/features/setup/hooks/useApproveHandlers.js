import { useCallback } from 'react'
import { withBase, fetchArtifactManifest, fetchArtifactHead } from '@/api/client'

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

export function useApproveHandler({
  preview, previewKind, previewUploadsBase, templateKind,
  file, tplName, tplDesc, tplTags,
  setCacheKey, setHtmlUrls, setPreview, addTemplate, setLastApprovedTemplate,
  toast, setSetupStep, mappingBtnRef,
}) {
  return useCallback(async (resp) => {
    const tplId = preview?.templateId
    const stripQuery = (url) => (url ? url.split('?')[0] : url)
    const refinedFinal = resp?.final_html_url ? withBase(stripQuery(resp.final_html_url)) : null
    const refinedTemplate = resp?.template_html_url ? withBase(stripQuery(resp.template_html_url)) : null
    let manifest = resp?.manifest || null

    if (!manifest && tplId) {
      try {
        manifest = await fetchArtifactManifest(tplId, { kind: previewKind })
      } catch (err) {
        console.warn('manifest fetch failed', err)
      }
    }

    const producedAtRaw = manifest?.produced_at
    const cacheSeed = producedAtRaw ? Date.parse(producedAtRaw) || producedAtRaw : Date.now()
    setCacheKey(cacheSeed)

    const buildFromManifest = (name) => {
      if (!tplId) return null
      const rel = manifest?.files?.[name]
      if (!rel) return null
      return withBase(`${previewUploadsBase}/${tplId}/${rel}`)
    }

    const templateBase = buildFromManifest('template_p1.html') || refinedTemplate || (preview?.htmlUrl ? stripQuery(preview.htmlUrl) : null)
    const llm2Base =
      buildFromManifest('template_llm2.html') ||
      (preview?.llm2HtmlUrl ? stripQuery(preview.llm2HtmlUrl) : null) ||
      templateBase
    const finalBase = buildFromManifest('report_final.html') || refinedFinal || templateBase

    let thumbnailBase =
      buildFromManifest('report_final.png') ||
      (resp?.thumbnail_url ? withBase(stripQuery(resp.thumbnail_url)) : null) ||
      preview?.pngUrl ||
      null

    if (tplId && thumbnailBase) {
      try {
        const head = await fetchArtifactHead(tplId, 'report_final.png', { kind: previewKind })
        if (!head?.artifact?.exists) {
          thumbnailBase = null
        }
      } catch (err) {
        console.warn('thumbnail head failed', err)
      }
    }

    const templateUrl = templateBase ? withCache(templateBase, cacheSeed) : null
    const llm2Url = llm2Base ? withCache(llm2Base, cacheSeed) : templateUrl
    const finalUrl = finalBase ? withCache(finalBase, cacheSeed) : templateUrl
    const thumbnailUrl = thumbnailBase ? withCache(thumbnailBase, cacheSeed) : null

    const normalizedKeys = Array.isArray(resp?.keys)
      ? Array.from(
          new Set(
            resp.keys
              .map((token) => (typeof token === 'string' ? token.trim() : ''))
              .filter(Boolean),
          ),
        )
      : []

    const artifacts =
      resp?.artifacts && typeof resp.artifacts === 'object' && !Array.isArray(resp.artifacts)
        ? resp.artifacts
        : undefined

    if (templateUrl || finalUrl || llm2Url) {
      setHtmlUrls({
        template: templateUrl || llm2Url || finalUrl,
        llm2: llm2Url || templateUrl || finalUrl,
        final: finalUrl || templateUrl || llm2Url,
      })
      setPreview((p) => ({
        ...p,
        htmlUrl: finalUrl || templateUrl || p?.htmlUrl,
        llm2HtmlUrl: llm2Url || templateUrl || p?.llm2HtmlUrl,
        pngUrl: thumbnailUrl || p?.pngUrl,
        keys: normalizedKeys,
      }))
    }

    const resolvedTemplateKind = previewKind || templateKind || 'pdf'
    const tpl = {
      id: tplId || `tpl_${Date.now()}`,
      name: tplName || file?.name || 'Template',
      status: 'approved',
      sourceType: resolvedTemplateKind,
      kind: resolvedTemplateKind,
      tags: tplTags ? tplTags.split(',').map((s) => s.trim()).filter(Boolean) : [],
      description: tplDesc || '',
      htmlUrl: finalUrl || templateUrl || undefined,
      thumbnailUrl: thumbnailUrl || undefined,
      mappingKeys: normalizedKeys,
      artifacts,
    }
    addTemplate(tpl)
    setLastApprovedTemplate(tpl)

    toast.show('Template approved and saved', 'success')
    setSetupStep('upload')
    mappingBtnRef.current?.focus()
  }, [
    preview, previewKind, previewUploadsBase, templateKind,
    file, tplName, tplDesc, tplTags,
    setCacheKey, setHtmlUrls, setPreview, addTemplate, setLastApprovedTemplate,
    toast, setSetupStep, mappingBtnRef,
  ])
}

export function useCorrectionsHandler({
  previewKind, previewTemplateId, templateId, setCacheKey, setHtmlUrls, setPreview,
}) {
  return useCallback(
    (payload) => {
      if (!payload) return

      const cacheSeed = payload.cache_key || Date.now()
      setCacheKey(cacheSeed)

      const templateHtmlRaw = payload?.artifacts?.template_html || null
      const pageSummaryRaw = payload?.artifacts?.page_summary || null

      const templateUrl = templateHtmlRaw ? withCache(templateHtmlRaw, cacheSeed) : null
      const pageSummaryUrl = pageSummaryRaw ? withCache(pageSummaryRaw, cacheSeed) : null

      if (templateUrl) {
        setHtmlUrls((prev) => ({
          ...prev,
          template: templateUrl,
          llm2: templateUrl,
        }))
      }

      const fallbackTemplateId = previewTemplateId || payload?.template_id || templateId || null

      setPreview((prev) => {
        const hasPrevious = !!prev
        if (!hasPrevious && !templateUrl && !pageSummaryUrl) {
          return prev
        }
        const next = hasPrevious ? { ...prev } : {}
        if (!hasPrevious && fallbackTemplateId) {
          next.templateId = fallbackTemplateId
        }
        if (!hasPrevious) {
          next.kind = previewKind
        }
        if (templateUrl) {
          next.htmlUrl = templateUrl
          next.llm2HtmlUrl = templateUrl
        }
        if (pageSummaryUrl) {
          next.pageSummaryUrl = pageSummaryUrl
        }
        next.previewTs = cacheSeed
        next.manifest_produced_at = cacheSeed
        return next
      })
    },
    [previewKind, previewTemplateId, templateId, setCacheKey, setHtmlUrls, setPreview],
  )
}
