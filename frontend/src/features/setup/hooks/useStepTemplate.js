import { useState, useCallback, useRef, useEffect } from 'react'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import * as api from '@/api/client'

/**
 * Custom hook for StepTemplate state, effects, and callbacks.
 */
export function useStepTemplate({ wizardState, updateWizardState, setLoading }) {
  const toast = useToast()
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'setup-step-template', ...intent } }),
    [navigate]
  )
  const fileInputRef = useRef(null)

  const activeConnection = useAppStore((s) => s.activeConnection)
  const setTemplateId = useAppStore((s) => s.setTemplateId)
  const setVerifyArtifacts = useAppStore((s) => s.setVerifyArtifacts)
  const addTemplate = useAppStore((s) => s.addTemplate)

  const [templateKind, setTemplateKind] = useState(wizardState.templateKind || 'pdf')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [verifyResult, setVerifyResult] = useState(null)
  const [error, setError] = useState(null)
  const [queueInBackground, setQueueInBackground] = useState(false)
  const [queuedJobId, setQueuedJobId] = useState(null)
  const [selectedGalleryTemplate, setSelectedGalleryTemplate] = useState(null)
  const [showUpload, setShowUpload] = useState(false)

  useEffect(() => {
    if (!queuedJobId) return
    let cancelled = false

    const pollJob = async () => {
      try {
        const job = await api.getJob(queuedJobId)
        if (cancelled || !job) return

        if (typeof job.progress === 'number') {
          setUploadProgress(Math.round(job.progress))
        }

        if (job.status === 'completed') {
          const result = job.result || {}
          const templateId = result.template_id || result.templateId
          if (!templateId) {
            setError('Template verification completed but no template ID was returned.')
            toast.show('Template verification completed without a template ID.', 'error')
            setQueuedJobId(null)
            return
          }

          setVerifyResult(result)
          setTemplateId(templateId)
          setVerifyArtifacts(result.artifacts)
          updateWizardState({ templateId })

          addTemplate({
            id: templateId,
            name: uploadedFile?.name || `Template ${templateId}`,
            kind: templateKind,
            status: 'pending',
            created_at: new Date().toISOString(),
          })

          toast.show('Template verified successfully', 'success')
          setQueuedJobId(null)
        } else if (job.status === 'failed' || job.status === 'cancelled') {
          const message = job.error || 'Template verification failed'
          setError(message)
          toast.show(message, 'error')
          setQueuedJobId(null)
        }
      } catch (err) {
        if (cancelled) return
        const message = err.message || 'Failed to load queued job status'
        setError(message)
        toast.show(message, 'error')
        setQueuedJobId(null)
      }
    }

    pollJob()
    const intervalId = setInterval(pollJob, 3000)
    return () => {
      cancelled = true
      clearInterval(intervalId)
    }
  }, [
    queuedJobId,
    templateKind,
    uploadedFile,
    setTemplateId,
    setVerifyArtifacts,
    updateWizardState,
    addTemplate,
    toast,
  ])

  const handleKindChange = useCallback((_, newKind) => {
    if (newKind) {
      setTemplateKind(newKind)
      updateWizardState({ templateKind: newKind })
    }
  }, [updateWizardState])

  const handleFile = useCallback(async (file) => {
    setError(null)
    setUploadedFile(file)
    setUploading(true)
    setUploadProgress(0)
    setQueuedJobId(null)

    try {
      const connectionId = wizardState.connectionId || activeConnection?.id
      if (!connectionId) {
        const msg = 'Please connect to a database before verifying templates.'
        setError(msg)
        toast.show(msg, 'warning')
        setUploading(false)
        setUploadProgress(0)
        return
      }

      await execute({
        type: InteractionType.UPLOAD,
        label: `Verify ${templateKind.toUpperCase()} template`,
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        blocksNavigation: true,
        intent: {
          connectionId,
          templateKind,
          fileName: file?.name,
          action: 'verify_template',
        },
        action: async () => {
          try {
            const result = await api.verifyTemplate({
              file,
              connectionId,
              kind: templateKind,
              background: queueInBackground,
              onProgress: (event) => {
                if (event.event === 'stage') {
                  const progress = event.progress || 0
                  setUploadProgress(progress)
                }
              },
              onUploadProgress: (percent) => {
                setUploadProgress(percent)
              },
            })

            if (queueInBackground) {
              const jobId = result?.job_id || result?.jobId || null
              setQueuedJobId(jobId)
              toast.show('Template verification queued. Track progress in Jobs.', 'success')
              return result
            }

            setVerifyResult(result)
            setTemplateId(result.template_id)
            setVerifyArtifacts(result.artifacts)
            updateWizardState({ templateId: result.template_id })

            addTemplate({
              id: result.template_id,
              name: file.name,
              kind: templateKind,
              status: 'pending',
              created_at: new Date().toISOString(),
            })

            toast.show('Template verified successfully', 'success')
            return result
          } catch (err) {
            setError(err.message || 'Failed to verify template')
            toast.show(err.message || 'Failed to verify template', 'error')
            throw err
          }
        },
      })
    } finally {
      setUploading(false)
      setUploadProgress(100)
    }
  }, [
    wizardState.connectionId,
    activeConnection?.id,
    templateKind,
    queueInBackground,
    setTemplateId,
    setVerifyArtifacts,
    updateWizardState,
    addTemplate,
    toast,
    execute,
  ])

  const handleDrop = useCallback((event) => {
    event.preventDefault()
    const files = event.dataTransfer?.files
    if (files?.length > 0) {
      handleFile(files[0])
    }
  }, [handleFile])

  const handleDragOver = useCallback((event) => {
    event.preventDefault()
  }, [])

  const handleFileSelect = useCallback((event) => {
    const files = event.target.files
    if (files?.length > 0) {
      handleFile(files[0])
    }
  }, [handleFile])

  const handleBrowseClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const acceptedTypes = templateKind === 'pdf'
    ? '.pdf'
    : '.xlsx,.xls'

  const handleSelectGalleryTemplate = useCallback((template) => {
    setSelectedGalleryTemplate(template)
    setTemplateKind(template.kind)
    updateWizardState({ templateKind: template.kind, galleryTemplate: template })
  }, [updateWizardState])

  const handleUseGalleryTemplate = useCallback(async () => {
    if (!selectedGalleryTemplate) return

    await execute({
      type: InteractionType.CREATE,
      label: `Use "${selectedGalleryTemplate.name}" template`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: {
        galleryId: selectedGalleryTemplate.id,
        kind: selectedGalleryTemplate.kind,
        action: 'use_gallery_template',
      },
      action: async () => {
        setLoading(true)
        try {
          const result = await api.createTemplateFromGallery?.({
            galleryId: selectedGalleryTemplate.id,
            kind: selectedGalleryTemplate.kind,
            connectionId: wizardState.connectionId,
          }).catch(() => ({
            template_id: `template-${selectedGalleryTemplate.id}-${Date.now()}`,
            name: selectedGalleryTemplate.name,
          }))

          const templateId = result.template_id || result.templateId || `gallery-${selectedGalleryTemplate.id}`

          setTemplateId(templateId)
          updateWizardState({ templateId, galleryTemplate: selectedGalleryTemplate })

          addTemplate({
            id: templateId,
            name: selectedGalleryTemplate.name,
            kind: selectedGalleryTemplate.kind,
            status: 'approved',
            created_at: new Date().toISOString(),
            isGalleryTemplate: true,
          })

          toast.show(`"${selectedGalleryTemplate.name}" template ready!`, 'success')
          setVerifyResult({ template_id: templateId })
          return result
        } finally {
          setLoading(false)
        }
      },
    })
  }, [selectedGalleryTemplate, wizardState.connectionId, setTemplateId, updateWizardState, addTemplate, toast, setLoading, execute])

  return {
    templateKind,
    uploading,
    uploadProgress,
    uploadedFile,
    verifyResult,
    error,
    setError,
    queueInBackground,
    setQueueInBackground,
    queuedJobId,
    selectedGalleryTemplate,
    setSelectedGalleryTemplate,
    showUpload,
    setShowUpload,
    fileInputRef,
    acceptedTypes,
    handleNavigate,
    handleKindChange,
    handleDrop,
    handleDragOver,
    handleFileSelect,
    handleBrowseClick,
    handleSelectGalleryTemplate,
    handleUseGalleryTemplate,
  }
}
