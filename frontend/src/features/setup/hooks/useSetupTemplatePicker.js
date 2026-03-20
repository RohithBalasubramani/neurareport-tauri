import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  isMock,
  listApprovedTemplates,
  deleteTemplate as deleteTemplateRequest,
  importTemplateZip,
  templateExportZipUrl,
} from '@/api/client'
import * as mock from '@/api/mock'
import { savePersistedCache } from '@/hooks/useBootstrapState.js'
import { useAppStore } from '@/stores'
import { confirmDelete } from '@/utils/confirmDelete'
import { useToast } from '@/components/ToastProvider.jsx'
import { resolveTemplatePreviewUrl, resolveTemplateThumbnailUrl } from '@/utils/preview'
import { getTemplateKind } from '../utils/templatesPaneUtils'

export function useSetupTemplatePicker({ selected, onToggle }) {
  const { templates, setTemplates, removeTemplate, setSetupNav } = useAppStore()
  const toast = useToast()
  const queryClient = useQueryClient()

  const [deleting, setDeleting] = useState(null)
  const [importing, setImporting] = useState(false)
  const [nameQuery, setNameQuery] = useState('')
  const fileInputRef = useRef(null)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewSrc, setPreviewSrc] = useState(null)
  const [previewType, setPreviewType] = useState('html')
  const [previewKey, setPreviewKey] = useState(null)

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['templates'],
    queryFn: () => (isMock ? mock.listTemplates() : listApprovedTemplates()),
  })

  useEffect(() => {
    if (data) {
      setTemplates(data)
      const state = useAppStore.getState()
      savePersistedCache({
        connections: state.savedConnections,
        templates: data,
        lastUsed: state.lastUsed,
      })
    }
  }, [data, setTemplates])

  const approved = useMemo(() => templates.filter((t) => t.status === 'approved'), [templates])

  const allTags = useMemo(() => Array.from(new Set(approved.flatMap((t) => t.tags || []))), [approved])

  const getFiltered = useCallback(
    (tagFilter) => {
      const tagFiltered = tagFilter.length
        ? approved.filter((t) => (t.tags || []).some((tag) => tagFilter.includes(tag)))
        : approved
      const nq = nameQuery.trim().toLowerCase()
      return nq ? tagFiltered.filter((t) => (t.name || '').toLowerCase().includes(nq)) : tagFiltered
    },
    [approved, nameQuery],
  )

  const handleImportFile = useCallback(
    async (file) => {
      if (!file) return
      if (isMock) {
        toast.show('Import is unavailable while using mock data.', 'info')
        return
      }
      setImporting(true)
      try {
        const baseName = file.name ? file.name.replace(/\.zip$/i, '').trim() : ''
        const result = await importTemplateZip({ file, name: baseName || undefined })
        await queryClient.invalidateQueries({ queryKey: ['templates'] })
        toast.show(`Imported "${result?.name || baseName || file.name}"`, 'success')
      } catch (err) {
        toast.show(String(err), 'error')
      } finally {
        setImporting(false)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }
    },
    [toast, queryClient],
  )

  const handleImportClick = useCallback(() => {
    if (isMock) {
      toast.show('Import is unavailable while using mock data.', 'info')
      return
    }
    fileInputRef.current?.click()
  }, [toast])

  const handleImportInputChange = useCallback(
    (event) => {
      const nextFile = event?.target?.files?.[0]
      if (nextFile) {
        handleImportFile(nextFile)
      }
    },
    [handleImportFile],
  )

  const handleThumbClick = (event, payload) => {
    event.stopPropagation()
    const url = payload?.url
    if (!url) return
    setPreviewSrc(url)
    setPreviewType(payload?.type || 'html')
    setPreviewKey(payload?.key || url)
    setPreviewOpen(true)
  }

  const handlePreviewClose = () => {
    setPreviewOpen(false)
    setPreviewSrc(null)
    setPreviewType('html')
    setPreviewKey(null)
  }

  const handleDeleteTemplate = async (template) => {
    if (!template?.id) return
    const name = template.name || template.id
    if (typeof window !== 'undefined') {
      const confirmed = confirmDelete(`Delete template "${name}"? This action cannot be undone.`)
      if (!confirmed) return
    }
    setDeleting(template.id)
    try {
      await deleteTemplateRequest(template.id)
      removeTemplate(template.id)
      if (selected.includes(template.id)) {
        onToggle(template.id)
      }
      queryClient.setQueryData(['templates'], (prev) => {
        if (Array.isArray(prev)) {
          return prev.filter((tpl) => tpl?.id !== template.id)
        }
        return prev
      })
      const state = useAppStore.getState()
      savePersistedCache({
        connections: state.savedConnections,
        templates: state.templates,
        lastUsed: state.lastUsed,
      })
      toast.show(`Deleted "${name}"`, 'success')
    } catch (err) {
      toast.show(String(err), 'error')
    } finally {
      setDeleting(null)
    }
  }

  const getTemplateCardData = useCallback((t) => {
    const previewInfo = resolveTemplatePreviewUrl(t)
    const thumbnailInfo = resolveTemplateThumbnailUrl(t)
    const htmlPreview = previewInfo.url
    const imagePreview = !htmlPreview ? thumbnailInfo.url : null
    const boxClickable = Boolean(htmlPreview || imagePreview)
    const mappingKeyCount = Array.isArray(t?.mappingKeys) ? t.mappingKeys.length : 0
    const exportHref = isMock ? null : templateExportZipUrl(t.id)
    const type = getTemplateKind(t).toUpperCase()
    return {
      previewInfo,
      htmlPreview,
      imagePreview,
      boxClickable,
      mappingKeyCount,
      exportHref,
      type,
    }
  }, [])

  return {
    templates,
    isLoading,
    isFetching,
    deleting,
    importing,
    nameQuery,
    setNameQuery,
    fileInputRef,
    previewOpen,
    previewSrc,
    previewType,
    previewKey,
    approved,
    allTags,
    getFiltered,
    setSetupNav,
    handleImportClick,
    handleImportInputChange,
    handleThumbClick,
    handlePreviewClose,
    handleDeleteTemplate,
    getTemplateCardData,
    selected,
    onToggle,
  }
}
