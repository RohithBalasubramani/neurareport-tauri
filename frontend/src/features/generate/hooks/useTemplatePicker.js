import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { savePersistedCache } from '@/hooks/useBootstrapState.js'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { confirmDelete } from '@/utils/confirmDelete'
import {
  deleteTemplateRequest,
  exportTemplateZip,
  getTemplateCatalog,
  importTemplateZip,
  isMock,
  listApprovedTemplates,
  mock,
  recommendTemplates,
  queueRecommendTemplates,
} from '../services/generateApi'

export function useTemplatePicker({ selected, onToggle, setOutputFormats }) {
  const templates = useAppStore((state) => state.templates)
  const templateCatalog = useAppStore((state) => state.templateCatalog)
  const setTemplates = useAppStore((state) => state.setTemplates)
  const setTemplateCatalog = useAppStore((state) => state.setTemplateCatalog)
  const removeTemplate = useAppStore((state) => state.removeTemplate)
  const queryClient = useQueryClient()
  const toast = useToast()

  const [deleting, setDeleting] = useState(null)
  const [activeTab, setActiveTab] = useState('all')
  const [nameQuery, setNameQuery] = useState('')
  const [showStarterInAll, setShowStarterInAll] = useState(true)
  const [requirement, setRequirement] = useState('')
  const [kindHints, setKindHints] = useState([])
  const [domainHints, setDomainHints] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [recommending, setRecommending] = useState(false)
  const [queueingRecommendations, setQueueingRecommendations] = useState(false)
  const [importing, setImporting] = useState(false)
  const [exporting, setExporting] = useState(null)
  const importInputRef = useRef(null)

  const templatesQuery = useQuery({
    queryKey: ['templates', isMock],
    queryFn: () => (isMock ? mock.listTemplates() : listApprovedTemplates()),
  })

  const catalogQuery = useQuery({
    queryKey: ['template-catalog', isMock],
    queryFn: () => {
      if (isMock) {
        return typeof mock.getTemplateCatalog === 'function' ? mock.getTemplateCatalog() : []
      }
      return getTemplateCatalog()
    },
  })

  const { data, isLoading, isFetching, isError, error } = templatesQuery
  const catalogData = catalogQuery.data

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

  useEffect(() => {
    if (catalogData) {
      setTemplateCatalog(catalogData)
    }
  }, [catalogData, setTemplateCatalog])

  const approved = useMemo(() => templates.filter((t) => t.status === 'approved'), [templates])
  const catalogPool = useMemo(
    () => (templateCatalog && templateCatalog.length ? templateCatalog : templates),
    [templateCatalog, templates],
  )
  const companyCandidates = useMemo(
    () => approved.filter((tpl) => String(tpl.source || 'company').toLowerCase() !== 'starter'),
    [approved],
  )
  const starterCandidates = useMemo(
    () => catalogPool.filter((tpl) => String(tpl.source || '').toLowerCase() === 'starter'),
    [catalogPool],
  )
  const allTags = useMemo(
    () => Array.from(new Set(companyCandidates.flatMap((tpl) => tpl.tags || []))),
    [companyCandidates],
  )

  const normalizedQuery = nameQuery.trim().toLowerCase()
  const applyNameFilter = useCallback(
    (items) => {
      if (!normalizedQuery) return items
      return items.filter((tpl) => (tpl.name || tpl.id || '').toLowerCase().includes(normalizedQuery))
    },
    [normalizedQuery],
  )
  const applyTagFilter = useCallback(
    (items, tagFilter) => {
      if (!tagFilter?.length) return items
      return items.filter((tpl) => (tpl.tags || []).some((tag) => tagFilter.includes(tag)))
    },
    [],
  )

  const kindOptions = useMemo(
    () =>
      Array.from(
        new Set(
          catalogPool
            .map((tpl) => (tpl.kind || '').toLowerCase())
            .filter(Boolean),
        ),
      ),
    [catalogPool],
  )
  const domainOptions = useMemo(
    () =>
      Array.from(
        new Set(
          catalogPool
            .map((tpl) => (tpl.domain || '').trim())
            .filter(Boolean),
        ),
      ),
    [catalogPool],
  )

  const recommendTemplatesClient = isMock ? mock.recommendTemplates : recommendTemplates

  const handleRecommend = async () => {
    const prompt = requirement.trim()
    if (!prompt) {
      toast.show('Describe what you need before requesting recommendations.', 'info')
      return
    }
    setRecommending(true)
    try {
      const result = await recommendTemplatesClient({
        requirement: prompt,
        limit: 6,
        kinds: kindHints,
        domains: domainHints,
      })
      const recs = Array.isArray(result?.recommendations)
        ? result.recommendations
        : Array.isArray(result)
          ? result
          : []
      setRecommendations(recs)
      setActiveTab('recommended')
    } catch (err) {
      toast.show(String(err), 'error')
    } finally {
      setRecommending(false)
    }
  }

  const handleQueueRecommend = async () => {
    const prompt = requirement.trim()
    if (!prompt) {
      toast.show('Describe what you need before queueing recommendations.', 'info')
      return
    }
    setQueueingRecommendations(true)
    try {
      const response = await queueRecommendTemplates({
        requirement: prompt,
        limit: 6,
        kinds: kindHints,
        domains: domainHints,
      })
      if (response?.job_id) {
        toast.show('Recommendation job queued. Track it in Jobs.', 'success')
      } else {
        toast.show('Failed to queue recommendations.', 'error')
      }
    } catch (err) {
      toast.show(String(err), 'error')
    } finally {
      setQueueingRecommendations(false)
    }
  }

  const handleRequirementKeyDown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      handleRecommend()
    }
  }

  const handleFindInAll = (templateName) => {
    const value = templateName || ""
    setNameQuery(value)
    setShowStarterInAll(true)
    setActiveTab('all')
  }

  const handleDeleteTemplate = async (template) => {
    if (!template?.id) return
    const name = template.name || template.id
    const confirmed = confirmDelete(`Delete "${name}"? This cannot be undone.`)
    if (!confirmed) return
    setDeleting(template.id)
    try {
      await deleteTemplateRequest(template.id)
      removeTemplate(template.id)
      setOutputFormats((prev) => {
        const next = { ...(prev || {}) }
        delete next[template.id]
        return next
      })
      if (selected.includes(template.id)) {
        onToggle(template.id)
      }
      queryClient.setQueryData(['templates', isMock], (prev) => {
        if (Array.isArray(prev)) {
          return prev.filter((item) => item?.id !== template.id)
        }
        if (prev && Array.isArray(prev.templates)) {
          return {
            ...prev,
            templates: prev.templates.filter((item) => item?.id !== template.id),
          }
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

  const handleImportTemplate = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const result = await importTemplateZip({ file, name: file.name.replace(/\.zip$/i, '') })
      toast.show(`Imported template "${result.name || result.template_id}"`, 'success')
      queryClient.invalidateQueries(['templates', isMock])
      queryClient.invalidateQueries(['template-catalog', isMock])
    } catch (err) {
      toast.show(`Import failed: ${err}`, 'error')
    } finally {
      setImporting(false)
      if (importInputRef.current) {
        importInputRef.current.value = ''
      }
    }
  }

  const handleExportTemplate = async (template) => {
    if (!template?.id) return
    setExporting(template.id)
    try {
      await exportTemplateZip(template.id)
      toast.show(`Exported "${template.name || template.id}"`, 'success')
    } catch (err) {
      toast.show(`Export failed: ${err}`, 'error')
    } finally {
      setExporting(null)
    }
  }

  const handleNameQueryChange = (value) => {
    setNameQuery(value)
    setShowStarterInAll(!value.trim())
  }

  return {
    // Query state
    isLoading,
    isFetching,
    isError,
    error,
    catalogQuery,
    // UI state
    deleting,
    activeTab,
    setActiveTab,
    nameQuery,
    showStarterInAll,
    requirement,
    setRequirement,
    kindHints,
    setKindHints,
    domainHints,
    setDomainHints,
    recommendations,
    recommending,
    queueingRecommendations,
    importing,
    exporting,
    importInputRef,
    // Derived data
    companyCandidates,
    starterCandidates,
    allTags,
    applyNameFilter,
    applyTagFilter,
    kindOptions,
    domainOptions,
    // Handlers
    handleRecommend,
    handleQueueRecommend,
    handleRequirementKeyDown,
    handleFindInAll,
    handleDeleteTemplate,
    handleImportTemplate,
    handleExportTemplate,
    handleNameQueryChange,
    // Toast
    toast,
  }
}
