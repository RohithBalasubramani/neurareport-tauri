import { useState, useCallback, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import * as api from '@/api/client'

export default function useReportConfig({ startDate, endDate } = {}) {
  const [searchParams] = useSearchParams()
  const toast = useToast()

  const templates = useAppStore((s) => s.templates)
  const activeConnection = useAppStore((s) => s.activeConnection)
  const setActiveConnectionId = useAppStore((s) => s.setActiveConnectionId)
  const setTemplates = useAppStore((s) => s.setTemplates)

  const [selectedTemplate, setSelectedTemplate] = useState(searchParams.get('template') || '')
  const [keyValues, setKeyValues] = useState({})
  const [keyOptions, setKeyOptions] = useState({})
  const [loading, setLoading] = useState(false)

  const keyOptionsRequestIdRef = useRef(0)

  const selectedTemplateInfo = templates.find((t) => t.id === selectedTemplate)
  const outputLabel = selectedTemplateInfo?.kind?.toUpperCase() || 'PDF'
  const keyFields = Object.keys(keyOptions)

  // Auto-select first template when templates are loaded but none selected
  useEffect(() => {
    if (!selectedTemplate && templates.length > 0) {
      setSelectedTemplate(templates[0].id)
    }
  }, [templates, selectedTemplate])

  useEffect(() => {
    const fetchTemplates = async () => {
      setLoading(true)
      try {
        const data = await api.listApprovedTemplates()
        setTemplates(data)
      } catch (err) {
        toast.show(err.message || 'Failed to load designs', 'error')
      } finally {
        setLoading(false)
      }
    }
    if (templates.length === 0) {
      fetchTemplates()
    }
  }, [templates.length, setTemplates, toast])

  useEffect(() => {
    const fetchKeyOptions = async () => {
      if (!selectedTemplate || !activeConnection?.id) return

      const requestId = ++keyOptionsRequestIdRef.current

      try {
        const template = templates.find((t) => t.id === selectedTemplate)
        const result = await api.fetchTemplateKeyOptions(selectedTemplate, {
          connectionId: activeConnection.id,
          kind: template?.kind || 'pdf',
          startDate: startDate || undefined,
          endDate: endDate || undefined,
        })

        if (requestId === keyOptionsRequestIdRef.current) {
          setKeyOptions(result.keys || {})
          // Clear any key selections that are no longer valid for this date range
          setKeyValues((prev) => {
            const validKeys = result.keys || {}
            const updated = {}
            for (const [key, val] of Object.entries(prev)) {
              if (!(key in validKeys)) continue
              const available = validKeys[key] || []
              if (Array.isArray(val)) {
                const filtered = val.filter((v) => available.includes(v))
                if (filtered.length > 0) updated[key] = filtered
              } else if (available.includes(val)) {
                updated[key] = val
              }
            }
            return updated
          })
        }
      } catch (err) {
        if (requestId === keyOptionsRequestIdRef.current) {
          console.error('Failed to fetch key options:', err)
          toast.show('Could not load filter options. You can still generate reports.', 'warning')
        }
      }
    }
    fetchKeyOptions()
  }, [selectedTemplate, activeConnection?.id, templates, toast, startDate, endDate])

  const handleTemplateChange = useCallback((event) => {
    setSelectedTemplate(event.target.value)
    setKeyValues({})
  }, [])

  const handleAiSelectTemplate = useCallback((template) => {
    if (template?.id) {
      setSelectedTemplate(template.id)
      setKeyValues({})
      toast.show(`Selected: ${template.name || template.id}`, 'success')
    }
  }, [toast])

  const handleKeyValueChange = useCallback((key, value, allOptions) => {
    if (Array.isArray(value) && value.includes('__all__')) {
      const opts = allOptions || []
      const prev = Array.isArray(value) ? value.filter(v => v !== '__all__') : []
      const allSelected = prev.length >= opts.length
      setKeyValues((p) => ({ ...p, [key]: allSelected ? [] : [...opts] }))
    } else {
      setKeyValues((prev) => ({ ...prev, [key]: value }))
    }
  }, [])

  return {
    templates,
    activeConnection,
    setActiveConnectionId,
    selectedTemplate,
    setSelectedTemplate,
    selectedTemplateInfo,
    outputLabel,
    keyValues,
    keyOptions,
    keyFields,
    loading,
    handleTemplateChange,
    handleAiSelectTemplate,
    handleKeyValueChange,
  }
}
