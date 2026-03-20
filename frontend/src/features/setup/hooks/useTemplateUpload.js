import { useCallback, useRef, useState } from 'react'
import { verifyTemplate as apiVerifyTemplate } from '@/api/client'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

const getTemplateKind = (file) => {
  const name = file?.name?.toLowerCase() || ''
  if (name.endsWith('.pdf')) return 'pdf'
  if (name.endsWith('.xls') || name.endsWith('.xlsx')) return 'excel'
  return null
}

export function useTemplateUpload() {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)
  const toast = useToast()
  const { execute } = useInteraction()
  const {
    activeConnectionId,
    setTemplateId,
    setVerifyArtifacts,
    setTemplateKind,
  } = useAppStore()

  const onFileChange = useCallback((e) => {
    const selected = Array.from(e.target.files || [])
    if (selected.length && !getTemplateKind(selected[0])) {
      toast.show('Unsupported file type. Please upload a PDF or Excel template.', 'warning')
      return
    }
    setFiles(selected)
    setResult(null)
    setError(null)
    if (selected.length) {
      setTemplateKind(getTemplateKind(selected[0]) || 'pdf')
    }
  }, [setTemplateKind, toast])

  const handleDrop = useCallback((event) => {
    event.preventDefault()
    setIsDragging(false)
    const dropped = Array.from(event.dataTransfer?.files || [])
    if (!dropped.length) return
    if (!getTemplateKind(dropped[0])) {
      toast.show('Unsupported file type. Please upload a PDF or Excel template.', 'warning')
      return
    }
    setFiles(dropped)
    setResult(null)
    setError(null)
    setTemplateKind(getTemplateKind(dropped[0]) || 'pdf')
  }, [setTemplateKind, toast])

  const handleDragOver = useCallback((event) => {
    event.preventDefault()
  }, [])

  const handleDragEnter = useCallback((event) => {
    event.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleUpload = useCallback(async () => {
    const file = files[0]
    if (!file || uploading) return
    const kind = getTemplateKind(file)
    if (!kind) {
      toast.show('Unsupported file type. Please upload a PDF or Excel template.', 'warning')
      return
    }
    if (!activeConnectionId) {
      toast.show('Connect to a database before verifying templates.', 'warning')
      return
    }

    await execute({
      type: InteractionType.UPLOAD,
      label: 'Verify template',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionId: activeConnectionId,
        templateKind: kind,
        fileName: file?.name,
        action: 'verify_template',
      },
      action: async () => {
        setUploading(true)
        setUploadProgress(0)
        setError(null)
        setResult(null)

        try {
          const response = await apiVerifyTemplate({
            file,
            connectionId: activeConnectionId,
            kind,
            onUploadProgress: (percent) => setUploadProgress(percent),
          })
          setResult(response)
          setTemplateId(response?.template_id || null)
          setVerifyArtifacts(response?.artifacts || null)
          setTemplateKind(kind)
          toast.show('Template uploaded and verified', 'success')
          return response
        } catch (err) {
          const message = err?.message || 'Failed to upload template'
          setError(message)
          toast.show(message, 'error')
          throw err
        } finally {
          setUploading(false)
        }
      },
    })
  }, [activeConnectionId, execute, files, setTemplateId, setTemplateKind, setVerifyArtifacts, toast, uploading])

  return {
    files,
    uploading,
    uploadProgress,
    error,
    result,
    isDragging,
    inputRef,
    onFileChange,
    handleDrop,
    handleDragOver,
    handleDragEnter,
    handleDragLeave,
    handleUpload,
  }
}
