import { useCallback, useState } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { exportAnalysis } from '../services/enhancedAnalyzeApi'

export default function useAnalysisExport({ analysisId }) {
  const [exportMenuAnchor, setExportMenuAnchor] = useState(null)
  const [isExporting, setIsExporting] = useState(false)

  const toast = useToast()
  const { execute } = useInteraction()

  const handleExport = useCallback((format) => {
    if (!analysisId) return undefined

    return execute({
      type: InteractionType.DOWNLOAD,
      label: `Export analysis (${format.toUpperCase()})`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { analysisId, format },
      action: async () => {
        setExportMenuAnchor(null)
        setIsExporting(true)

        try {
          const blob = await exportAnalysis(analysisId, { format })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `analysis_${analysisId}.${format}`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
          toast.show(`Exported as ${format.toUpperCase()}`, 'success')
        } catch (err) {
          toast.show(err.message || 'Export failed', 'error')
        } finally {
          setIsExporting(false)
        }
      },
    })
  }, [analysisId, execute, toast])

  return {
    exportMenuAnchor,
    setExportMenuAnchor,
    isExporting,
    handleExport,
  }
}
