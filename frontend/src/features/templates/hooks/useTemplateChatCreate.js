/**
 * Custom hook for Template Chat Create state and actions.
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useToast } from '@/components/ToastProvider.jsx'
import {
  useInteraction,
  InteractionType,
  Reversibility,
  useNavigateInteraction,
} from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import { useTemplateChatStore } from '@/stores/templateChatStore'
import { chatTemplateCreate, createTemplateFromChat, mappingPreview, mappingApprove } from '@/api/client'

const MAX_PDF_SIZE_MB = 10
const SESSION_KEY = '__chat_create__'

export function useTemplateChatCreate() {
  const navigate = useNavigateInteraction()
  const toast = useToast()
  const { execute } = useInteraction()
  const addTemplate = useAppStore((s) => s.addTemplate)
  const setTemplateId = useAppStore((s) => s.setTemplateId)
  const lastUsedConnectionId = useAppStore((s) => s.lastUsed?.connectionId || null)
  const activeConnection = useAppStore((s) => s.activeConnection)
  const setActiveConnectionId = useAppStore((s) => s.setActiveConnectionId)
  const deleteSession = useTemplateChatStore((s) => s.deleteSession)
  const addAssistantMessage = useTemplateChatStore((s) => s.addAssistantMessage)
  const [searchParams] = useSearchParams()
  const fromWizard = searchParams.get('from') === 'wizard'
  const wizardConnectionId = searchParams.get('connectionId') || null

  const [selectedConnectionId, setSelectedConnectionId] = useState(
    wizardConnectionId || lastUsedConnectionId || activeConnection?.id || ''
  )
  const [currentHtml, setCurrentHtml] = useState('')
  const [previewUrl, setPreviewUrl] = useState(null)
  const [nameDialogOpen, setNameDialogOpen] = useState(false)
  const [templateName, setTemplateName] = useState('')
  const [creating, setCreating] = useState(false)
  const [samplePdf, setSamplePdf] = useState(null)
  const [templateKind, setTemplateKind] = useState('pdf')
  const fileInputRef = useRef(null)

  // Mapping phase state
  const [savedTemplateId, setSavedTemplateId] = useState(null)
  const [savedTemplateKind, setSavedTemplateKind] = useState('pdf')
  const [savedTemplateName, setSavedTemplateName] = useState('')
  const [mappingPreviewData, setMappingPreviewData] = useState(null)
  const [mappingApproving, setMappingApproving] = useState(false)

  const handleFileSelect = useCallback((file) => {
    if (!file) return
    const pdfTypes = ['application/pdf']
    const excelTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
    ]
    const allowedTypes = templateKind === 'excel' ? [...pdfTypes, ...excelTypes] : pdfTypes
    const isExcelExt = /\.(xlsx|xls)$/i.test(file.name)
    if (!allowedTypes.includes(file.type) && !(templateKind === 'excel' && isExcelExt)) {
      toast.show(templateKind === 'excel' ? 'Please upload a PDF or Excel file.' : 'Please upload a PDF file.', 'warning')
      return
    }
    if (file.size > MAX_PDF_SIZE_MB * 1024 * 1024) {
      toast.show(`File too large. Maximum size is ${MAX_PDF_SIZE_MB}MB.`, 'warning')
      return
    }
    setSamplePdf({ file, name: file.name, size: file.size })
    toast.show(`Sample file "${file.name}" attached. The AI will use this as a visual reference.`, 'info')
  }, [toast, templateKind])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    const file = e.dataTransfer?.files?.[0]
    handleFileSelect(file)
  }, [handleFileSelect])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
  }, [])

  const handleRemovePdf = useCallback(() => {
    setSamplePdf(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }, [])

  // Update preview when HTML changes
  useEffect(() => {
    if (!currentHtml) {
      setPreviewUrl(null)
      return
    }
    const blob = new Blob([currentHtml], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [currentHtml])

  // Clean up session on unmount
  useEffect(() => {
    return () => {
      // Don't clean up — let the user resume if they navigate back
    }
  }, [])

  const handleHtmlUpdate = useCallback((html) => {
    setCurrentHtml(html)
  }, [])

  const handleApplySuccess = useCallback((result) => {
    if (result?.updated_html) {
      setCurrentHtml(result.updated_html)
    }
  }, [])

  const handleBack = useCallback(async () => {
    const backTo = fromWizard ? '/setup?step=template' : '/templates'
    await navigate(backTo, {
      interaction: {
        type: InteractionType.NAVIGATE,
        label: fromWizard ? 'Back to wizard' : 'Back to templates',
        reversibility: Reversibility.FULLY_REVERSIBLE,
      },
    })
  }, [navigate, fromWizard])

  const handleOpenNameDialog = useCallback(() => {
    setNameDialogOpen(true)
  }, [])

  const handleCloseNameDialog = useCallback(() => {
    setNameDialogOpen(false)
  }, [])

  // Navigate to template editor (after save or after mapping)
  const navigateToTemplate = useCallback(async (templateId, name, kind) => {
    deleteSession(SESSION_KEY)
    if (fromWizard) {
      try {
        const wizardRaw = sessionStorage.getItem('neurareport_wizard_state')
        const wizardData = wizardRaw ? JSON.parse(wizardRaw) : {}
        wizardData.templateId = templateId
        wizardData.templateKind = kind
        wizardData.templateName = name
        sessionStorage.setItem('neurareport_wizard_state', JSON.stringify(wizardData))
      } catch (_) { /* ignore storage errors */ }

      await navigate('/setup?step=mapping', {
        interaction: {
          type: InteractionType.NAVIGATE,
          label: 'Continue to mapping',
          reversibility: Reversibility.FULLY_REVERSIBLE,
        },
      })
    } else {
      await navigate(`/templates/${templateId}/edit`, {
        state: { from: '/templates', editMode: 'chat' },
        interaction: {
          type: InteractionType.NAVIGATE,
          label: 'Open new template editor',
          reversibility: Reversibility.FULLY_REVERSIBLE,
        },
      })
    }
  }, [deleteSession, fromWizard, navigate])

  const handleCreateTemplate = useCallback(async () => {
    const name = templateName.trim()
    if (!name) {
      toast.show('Please enter a template name.', 'warning')
      return
    }
    if (!currentHtml) {
      toast.show('No template HTML to save. Continue the conversation to generate a template first.', 'warning')
      return
    }

    await execute({
      type: InteractionType.CREATE,
      label: 'Create template from chat',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { action: 'create_template_from_chat', name },
      action: async () => {
        setCreating(true)
        try {
          const result = await createTemplateFromChat(name, currentHtml, templateKind)
          const templateId = result?.template_id
          const kind = result?.kind || 'pdf'

          if (templateId) {
            addTemplate({
              id: templateId,
              name,
              kind,
              status: 'draft',
              artifacts: {},
              tags: [],
            })
            setTemplateId(templateId)
          }

          setNameDialogOpen(false)

          const connId = selectedConnectionId || wizardConnectionId || lastUsedConnectionId
          if (templateId && connId) {
            setSavedTemplateId(templateId)
            setSavedTemplateKind(kind)
            setSavedTemplateName(name)

            toast.show(`Template "${name}" saved! Fetching data mapping suggestions...`, 'info')
            addAssistantMessage(
              SESSION_KEY,
              `Template "${name}" has been saved successfully! Now let's configure how your template fields map to your database columns. Fetching mapping suggestions...`
            )

            try {
              const preview = await mappingPreview(templateId, connId, { kind })
              const mapping = preview?.mapping || preview?.auto_mapping || {}

              if (Object.keys(mapping).length > 0) {
                setMappingPreviewData(preview)
                addAssistantMessage(
                  SESSION_KEY,
                  `I've auto-mapped ${Object.keys(mapping).length} template fields to your database columns. Review the mapping below — you can click any value to change it, or type in the chat to discuss changes.`
                )
              } else {
                toast.show(`Template "${name}" saved. No auto-mapping available — you can configure mapping later.`, 'info')
                addAssistantMessage(
                  SESSION_KEY,
                  `Template saved, but I couldn't generate auto-mapping suggestions. You can configure mapping manually from the template editor.`
                )
                navigateToTemplate(templateId, name, kind)
              }
            } catch (mapErr) {
              console.warn('Mapping preview failed:', mapErr)
              toast.show(`Template "${name}" saved. Mapping preview failed — you can map manually later.`, 'warning')
              addAssistantMessage(
                SESSION_KEY,
                `Template saved! Auto-mapping encountered an issue, but you can configure it from the template editor.`
              )
              navigateToTemplate(templateId, name, kind)
            }
          } else {
            toast.show(`Template "${name}" created successfully.`, 'success')
            addAssistantMessage(
              SESSION_KEY,
              `Template "${name}" has been saved! Connect a database to enable field mapping.`
            )
            deleteSession(SESSION_KEY)
            navigateToTemplate(templateId, name, kind)
          }
        } catch (err) {
          toast.show(String(err.message || err), 'error')
          throw err
        } finally {
          setCreating(false)
        }
      },
    })
  }, [templateName, currentHtml, execute, addTemplate, setTemplateId, deleteSession, toast, navigate, fromWizard, wizardConnectionId, lastUsedConnectionId, addAssistantMessage, selectedConnectionId, navigateToTemplate, templateKind])

  const handleMappingApprove = useCallback(async (finalMapping) => {
    if (!savedTemplateId) return
    setMappingApproving(true)
    try {
      const connId = selectedConnectionId || wizardConnectionId || lastUsedConnectionId
      addAssistantMessage(SESSION_KEY, 'Building contract and generator assets... This may take a moment.')
      toast.show('Approving mapping and building contract...', 'info')
      await mappingApprove(savedTemplateId, finalMapping, {
        connectionId: connId,
        kind: savedTemplateKind,
      })
      toast.show(`Template "${savedTemplateName}" is report-ready!`, 'success')
      addAssistantMessage(SESSION_KEY, `Mapping approved and contract built! Template "${savedTemplateName}" is now report-ready. Redirecting...`)
      setTimeout(() => {
        navigateToTemplate(savedTemplateId, savedTemplateName, savedTemplateKind)
      }, 1500)
    } catch (err) {
      console.error('Mapping approve failed:', err)
      toast.show('Mapping approval failed. You can retry or map later from the editor.', 'error')
      addAssistantMessage(SESSION_KEY, `Mapping approval encountered an error: ${err.message || err}. You can try again or skip to map later.`)
    } finally {
      setMappingApproving(false)
    }
  }, [savedTemplateId, savedTemplateKind, savedTemplateName, wizardConnectionId, lastUsedConnectionId, toast, addAssistantMessage, navigateToTemplate, selectedConnectionId])

  const handleMappingSkip = useCallback(() => {
    if (!savedTemplateId) return
    toast.show(`Template "${savedTemplateName}" saved. You can configure mapping from the editor.`, 'info')
    navigateToTemplate(savedTemplateId, savedTemplateName, savedTemplateKind)
  }, [savedTemplateId, savedTemplateName, savedTemplateKind, toast, navigateToTemplate])

  const handleMappingQueue = useCallback(() => {
    if (!savedTemplateId) return
    const connId = selectedConnectionId || wizardConnectionId || lastUsedConnectionId
    mappingApprove(savedTemplateId, mappingPreviewData?.mapping || {}, {
      connectionId: connId,
      kind: savedTemplateKind,
    }).then(() => {}).catch((err) => {
      console.warn('Background mapping approval failed:', err)
    })
    toast.show(`Mapping approval queued for "${savedTemplateName}". You can check progress from the template editor.`, 'info')
    navigateToTemplate(savedTemplateId, savedTemplateName, savedTemplateKind)
  }, [savedTemplateId, savedTemplateName, savedTemplateKind, wizardConnectionId, lastUsedConnectionId, mappingPreviewData, toast, navigateToTemplate, selectedConnectionId])

  const chatApi = useCallback((messages, html) => {
    return chatTemplateCreate(messages, html, samplePdf?.file || null, templateKind)
  }, [samplePdf, templateKind])

  return {
    // State
    selectedConnectionId,
    setSelectedConnectionId,
    setActiveConnectionId,
    currentHtml,
    previewUrl,
    nameDialogOpen,
    templateName,
    setTemplateName,
    creating,
    samplePdf,
    templateKind,
    setTemplateKind,
    fileInputRef,
    mappingPreviewData,
    mappingApproving,
    fromWizard,
    // Handlers
    handleFileSelect,
    handleDrop,
    handleDragOver,
    handleRemovePdf,
    handleHtmlUpdate,
    handleApplySuccess,
    handleBack,
    handleOpenNameDialog,
    handleCloseNameDialog,
    handleCreateTemplate,
    handleMappingApprove,
    handleMappingSkip,
    handleMappingQueue,
    chatApi,
    SESSION_KEY,
  }
}
