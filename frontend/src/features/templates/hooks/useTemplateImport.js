/**
 * Hook: Import template from zip backup
 */
import { useState, useCallback } from 'react'
import { useToast } from '@/components/ToastProvider'
import {
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'
import * as api from '@/api/client'

export default function useTemplateImport({ fetchTemplatesData }) {
  const toast = useToast()
  const { execute } = useInteraction()

  const [importOpen, setImportOpen] = useState(false)
  const [importFile, setImportFile] = useState(null)
  const [importName, setImportName] = useState('')
  const [importing, setImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)

  const handleOpenImport = useCallback(() => {
    setImportOpen(true)
  }, [])

  const handleImport = useCallback(async () => {
    if (!importFile) {
      toast.show('Select a design backup file first', 'error')
      return
    }
    const fileName = importFile.name || ''
    const ext = fileName.toLowerCase().split('.').pop()
    if (ext !== 'zip') {
      toast.show('Invalid file type. Please select a .zip file', 'error')
      return
    }
    const maxSize = 50 * 1024 * 1024
    if (importFile.size > maxSize) {
      toast.show('File too large. Maximum size is 50MB', 'error')
      return
    }

    execute({
      type: InteractionType.UPLOAD,
      label: `Import design "${importName.trim() || fileName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      successMessage: 'Design imported',
      errorMessage: 'Failed to import design',
      action: async () => {
        setImporting(true)
        setImportProgress(0)
        try {
          await api.importTemplateZip({
            file: importFile,
            name: importName.trim() || undefined,
            onUploadProgress: (percent) => setImportProgress(percent),
          })
          await fetchTemplatesData()
          setImportOpen(false)
          setImportFile(null)
          setImportName('')
        } finally {
          setImporting(false)
          setImportProgress(0)
        }
      },
    })
  }, [importFile, importName, fetchTemplatesData, execute])

  return {
    importOpen,
    setImportOpen,
    importFile,
    setImportFile,
    importName,
    setImportName,
    importing,
    importProgress,
    handleOpenImport,
    handleImport,
  }
}
