import { useCallback, useEffect, useState } from 'react'
import {
  createSavedChart as createSavedChartRequest,
  deleteSavedChart as deleteSavedChartRequest,
  listSavedCharts as listSavedChartsRequest,
  updateSavedChart as updateSavedChartRequest,
} from '../services/generateApi'

export function useSavedCharts({ templateId, templateKind }) {
  const [savedCharts, setSavedCharts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const reset = useCallback(() => {
    setSavedCharts([])
    setLoading(false)
    setError(null)
  }, [])

  const fetchSavedCharts = useCallback(() => {
    if (!templateId) {
      reset()
      return
    }
    const currentTemplate = templateId
    setLoading(true)
    setError(null)
    listSavedChartsRequest({ templateId: currentTemplate, kind: templateKind })
      .then((charts) => {
        if (currentTemplate === templateId) {
          setSavedCharts(charts)
        }
      })
      .catch((err) => {
        if (currentTemplate === templateId) {
          setError(err?.message || 'Failed to load saved charts.')
        }
      })
      .finally(() => {
        if (currentTemplate === templateId) {
          setLoading(false)
        }
      })
  }, [reset, templateId, templateKind])

  useEffect(() => {
    fetchSavedCharts()
  }, [fetchSavedCharts])

  const createSavedChart = useCallback(
    async ({ name, spec }) => {
      if (!templateId) throw new Error('No template selected')
      const created = await createSavedChartRequest({
        templateId,
        name,
        spec,
        kind: templateKind,
      })
      setSavedCharts((prev) => [...prev, created])
      return created
    },
    [templateId, templateKind],
  )

  const renameSavedChart = useCallback(
    async ({ chartId, name }) => {
      if (!templateId) throw new Error('No template selected')
      const updated = await updateSavedChartRequest({
        templateId,
        chartId,
        name,
        kind: templateKind,
      })
      setSavedCharts((prev) => prev.map((item) => (item.id === updated.id ? updated : item)))
      return updated
    },
    [templateId, templateKind],
  )

  const deleteSavedChart = useCallback(
    async ({ chartId }) => {
      if (!templateId) throw new Error('No template selected')
      await deleteSavedChartRequest({
        templateId,
        chartId,
        kind: templateKind,
      })
      setSavedCharts((prev) => prev.filter((item) => item.id !== chartId))
    },
    [templateId, templateKind],
  )

  return {
    savedCharts,
    savedChartsLoading: loading,
    savedChartsError: error,
    fetchSavedCharts,
    createSavedChart,
    renameSavedChart,
    deleteSavedChart,
  }
}
