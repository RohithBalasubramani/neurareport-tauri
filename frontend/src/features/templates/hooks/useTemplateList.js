/**
 * Hook: Template list loading, tags, and favorites
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import * as api from '@/api/client'

export default function useTemplateList() {
  const toast = useToast()
  const templates = useAppStore((s) => s.templates)
  const setTemplates = useAppStore((s) => s.setTemplates)
  const removeTemplate = useAppStore((s) => s.removeTemplate)
  const updateTemplate = useAppStore((s) => s.updateTemplate)

  const [loading, setLoading] = useState(false)
  const [allTags, setAllTags] = useState([])
  const [favorites, setFavorites] = useState(new Set())
  const didLoadRef = useRef(false)

  const fetchTemplatesData = useCallback(async () => {
    setLoading(true)
    try {
      const [templatesData, tagsData, favoritesData] = await Promise.all([
        api.listTemplates(),
        api.getAllTemplateTags(),
        api.getFavorites().catch(() => ({ templates: [] })),
      ])
      setTemplates(templatesData)
      setAllTags(tagsData.tags || [])
      const favIds = (favoritesData.templates || []).map((t) => t.id)
      setFavorites(new Set(favIds))
    } catch (err) {
      toast.show(err.message || 'Failed to load designs', 'error')
    } finally {
      setLoading(false)
    }
  }, [setTemplates, toast])

  const handleFavoriteToggle = useCallback((templateId, isFavorite) => {
    setFavorites((prev) => {
      const next = new Set(prev)
      if (isFavorite) {
        next.add(templateId)
      } else {
        next.delete(templateId)
      }
      return next
    })
  }, [])

  useEffect(() => {
    if (didLoadRef.current) return
    didLoadRef.current = true
    fetchTemplatesData()
  }, [fetchTemplatesData])

  return {
    templates,
    setTemplates,
    removeTemplate,
    updateTemplate,
    loading,
    allTags,
    favorites,
    handleFavoriteToggle,
    fetchTemplatesData,
  }
}
