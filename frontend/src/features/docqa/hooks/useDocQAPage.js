/**
 * Custom hook: all state, effects, and handlers for the Document Q&A page.
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import { listReportRuns } from '@/api/client'
import useDocQAStore from '@/stores/docqaStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import {
  useInteraction,
  InteractionType,
  Reversibility,
  useConfirmedAction,
} from '@/components/ux/governance'
import {
  MAX_DOC_SIZE,
  MIN_DOC_LENGTH,
  MAX_NAME_LENGTH,
  MIN_QUESTION_LENGTH,
  MAX_QUESTION_LENGTH,
} from '../components/DocQAStyledComponents'

export function useDocQAPage() {
  const {
    sessions,
    currentSession,
    messages,
    loading,
    asking,
    error,
    fetchSessions,
    createSession,
    getSession,
    deleteSession,
    addDocument,
    removeDocument,
    askQuestion,
    clearHistory,
    submitFeedback,
    regenerateResponse,
    reset,
  } = useDocQAStore()

  const { connections, templates } = useSharedData()
  const toast = useToast()
  const { execute } = useInteraction()
  const confirmDeleteSession = useConfirmedAction('DELETE_SESSION')

  // Cross-page: accept incoming documents from other features
  useIncomingTransfer(FeatureKey.DOCQA, {
    [TransferAction.CHAT_WITH]: async (payload) => {
      const session = await createSession(payload.title ? `Q&A: ${payload.title}` : 'Q&A: Imported')
      if (session) {
        await addDocument(session.id, {
          name: payload.title || 'Imported Document',
          content: typeof payload.content === 'string' ? payload.content : JSON.stringify(payload.content),
        })
      }
    },
    [TransferAction.ADD_TO]: async (payload) => {
      if (currentSession) {
        await addDocument(currentSession.id, {
          name: payload.title || 'Imported Document',
          content: typeof payload.content === 'string' ? payload.content : JSON.stringify(payload.content),
        })
      }
    },
  })

  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [addDocDialogOpen, setAddDocDialogOpen] = useState(false)
  const [reportPickerOpen, setReportPickerOpen] = useState(false)
  const [availableRuns, setAvailableRuns] = useState([])
  const [runsLoading, setRunsLoading] = useState(false)
  const [newSessionName, setNewSessionName] = useState('')
  const [docName, setDocName] = useState('')
  const [docContent, setDocContent] = useState('')
  const [question, setQuestion] = useState('')
  const messagesEndRef = useRef(null)
  const [deleteSessionConfirm, setDeleteSessionConfirm] = useState({
    open: false,
    sessionId: null,
    sessionName: '',
  })
  const [removeDocConfirm, setRemoveDocConfirm] = useState({
    open: false,
    docId: null,
    docName: '',
  })
  const [clearChatConfirm, setClearChatConfirm] = useState({
    open: false,
    sessionId: null,
    sessionName: '',
    messageCount: 0,
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedConnectionId, setSelectedConnectionId] = useState('')
  const [initialLoading, setInitialLoading] = useState(true)
  const inputRef = useRef(null)
  const docCount = currentSession?.documents?.length || 0

  useEffect(() => {
    const init = async () => {
      setInitialLoading(true)
      await fetchSessions()
      setInitialLoading(false)
    }
    init()
    return () => reset()
  }, [fetchSessions, reset])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleCreateSession = () => {
    if (!newSessionName) return
    if (newSessionName.length > MAX_NAME_LENGTH) {
      toast.show(`Session name must be ${MAX_NAME_LENGTH} characters or less`, 'error')
      return
    }
    execute({
      type: InteractionType.CREATE,
      label: `Create session "${newSessionName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Session created successfully',
      action: async () => {
        await createSession(newSessionName)
        setCreateDialogOpen(false)
        setNewSessionName('')
      },
    })
  }

  const handleAddDocument = () => {
    if (!currentSession || !docName || !docContent) return
    if (docName.length > MAX_NAME_LENGTH) {
      toast.show(`Document name must be ${MAX_NAME_LENGTH} characters or less`, 'error')
      return
    }
    if (docContent.trim().length < MIN_DOC_LENGTH) {
      toast.show(`Document content must be at least ${MIN_DOC_LENGTH} characters`, 'error')
      return
    }
    if (docContent.length > MAX_DOC_SIZE) {
      toast.show('Document content exceeds 5MB limit', 'error')
      return
    }
    execute({
      type: InteractionType.UPLOAD,
      label: `Add document "${docName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Document added successfully',
      action: async () => {
        await addDocument(currentSession.id, {
          name: docName,
          content: docContent,
        })
        setAddDocDialogOpen(false)
        setDocName('')
        setDocContent('')
      },
    })
  }

  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (!file) return
    if (file.name.length > MAX_NAME_LENGTH) {
      toast.show(`File name must be ${MAX_NAME_LENGTH} characters or less`, 'error')
      event.target.value = ''
      return
    }

    const allowedExtensions = ['.txt', '.md', '.json', '.csv']
    const fileName = file.name.toLowerCase()
    const hasValidExtension = allowedExtensions.some((ext) =>
      fileName.endsWith(ext)
    )

    if (!hasValidExtension) {
      toast.show(
        `Invalid file type. Supported formats: ${allowedExtensions.join(', ')}`,
        'error'
      )
      event.target.value = ''
      return
    }

    if (file.size > MAX_DOC_SIZE) {
      toast.show('File size exceeds 5MB limit', 'error')
      event.target.value = ''
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target.result
      if (content.includes('\0')) {
        toast.show('File appears to be binary. Please upload a text file.', 'error')
        event.target.value = ''
        return
      }
      setDocName(file.name)
      setDocContent(content)
    }
    reader.onerror = () => {
      toast.show('Failed to read file', 'error')
      event.target.value = ''
    }
    reader.readAsText(file)
  }

  const handleOpenReportPicker = async () => {
    setReportPickerOpen(true)
    setRunsLoading(true)
    try {
      const runs = await listReportRuns({ limit: 50 })
      setAvailableRuns(runs.filter((r) => r.status === 'succeeded'))
    } catch {
      toast.show('Failed to load reports', 'error')
    } finally {
      setRunsLoading(false)
    }
  }

  const handleSelectReport = (run) => {
    if (!currentSession) return
    execute({
      type: InteractionType.UPLOAD,
      label: `Add report "${run.templateName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: `Report "${run.templateName}" added`,
      action: async () => {
        await addDocument(currentSession.id, {
          name: `${run.templateName} (${run.startDate} – ${run.endDate})`,
          content: [
            `Report: ${run.templateName}`,
            `Period: ${run.startDate} to ${run.endDate}`,
            `Connection: ${run.connectionName}`,
            `Generated: ${new Date(run.createdAt).toLocaleString()}`,
            `Status: ${run.status}`,
            run.artifacts?.html_url ? `HTML: ${run.artifacts.html_url}` : '',
            run.artifacts?.pdf_url ? `PDF: ${run.artifacts.pdf_url}` : '',
          ].filter(Boolean).join('\n'),
        })
        setReportPickerOpen(false)
      },
    })
  }

  const handleAskQuestion = () => {
    if (!currentSession || !question.trim()) return
    const trimmedQuestion = question.trim()
    if (trimmedQuestion.length < MIN_QUESTION_LENGTH) {
      toast.show(`Question must be at least ${MIN_QUESTION_LENGTH} characters`, 'error')
      return
    }
    if (trimmedQuestion.length > MAX_QUESTION_LENGTH) {
      toast.show(`Question must be ${MAX_QUESTION_LENGTH} characters or less`, 'error')
      return
    }
    const q = trimmedQuestion
    execute({
      type: InteractionType.ANALYZE,
      label: 'Analyzing documents...',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      action: async () => {
        setQuestion('')
        await askQuestion(currentSession.id, q)
      },
    })
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleAskQuestion()
    }
  }

  const handleCopyMessage = (content) => {
    navigator.clipboard.writeText(content)
    toast.show('Copied to clipboard', 'success')
  }

  const handleCitationClick = useCallback(async (citation) => {
    const text = citation?.quote || citation?.document_name
    if (!text) return
    if (!navigator?.clipboard?.writeText) {
      toast.show('Clipboard not available', 'warning')
      return
    }
    try {
      await navigator.clipboard.writeText(text)
      toast.show('Citation copied', 'success')
    } catch (err) {
      toast.show(err.message || 'Failed to copy citation', 'error')
    }
  }, [toast])

  const handleFeedback = async (messageId, feedbackType) => {
    if (!currentSession) return
    const result = await submitFeedback(currentSession.id, messageId, feedbackType)
    if (result) {
      toast.show(feedbackType === 'helpful' ? 'Thanks for the feedback!' : 'Thanks for letting us know', 'success')
    }
  }

  const handleRegenerate = (messageId) => {
    if (!currentSession) return
    execute({
      type: InteractionType.GENERATE,
      label: 'Regenerating response...',
      reversibility: Reversibility.SYSTEM_MANAGED,
      successMessage: 'Response regenerated',
      errorMessage: 'Failed to regenerate response',
      blocksNavigation: true,
      action: async () => {
        const result = await regenerateResponse(currentSession.id, messageId)
        if (!result) throw new Error('Regenerate failed')
      },
    })
  }

  const filteredSessions = sessions.filter((session) =>
    session.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const suggestedQuestions = [
    'What are the main topics covered in these documents?',
    'Can you summarize the key findings?',
    'What are the most important insights?',
    'Are there any conflicting information?',
  ]

  return {
    // Store data
    sessions,
    currentSession,
    messages,
    loading,
    asking,
    error,
    connections,
    templates,
    reset,

    // Session actions
    getSession,
    addDocument,

    // Dialog state
    createDialogOpen,
    setCreateDialogOpen,
    addDocDialogOpen,
    setAddDocDialogOpen,
    reportPickerOpen,
    setReportPickerOpen,
    availableRuns,
    runsLoading,
    newSessionName,
    setNewSessionName,
    docName,
    setDocName,
    docContent,
    setDocContent,
    question,
    setQuestion,

    // Confirm modals
    deleteSessionConfirm,
    setDeleteSessionConfirm,
    removeDocConfirm,
    setRemoveDocConfirm,
    clearChatConfirm,
    setClearChatConfirm,

    // Misc state
    searchQuery,
    setSearchQuery,
    selectedConnectionId,
    setSelectedConnectionId,
    initialLoading,
    messagesEndRef,
    inputRef,
    docCount,

    // Handlers
    handleCreateSession,
    handleAddDocument,
    handleFileUpload,
    handleOpenReportPicker,
    handleSelectReport,
    handleAskQuestion,
    handleKeyDown,
    handleCopyMessage,
    handleCitationClick,
    handleFeedback,
    handleRegenerate,

    // Derived
    filteredSessions,
    suggestedQuestions,

    // UX Governance
    execute,
    confirmDeleteSession,
  }
}
