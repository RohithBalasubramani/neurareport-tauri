/**
 * Custom hook: all state, effects, and callbacks for TemplateChatEditor.
 */
import { useState, useRef, useCallback, useEffect } from 'react'
import { useTemplateChatStore, DEFAULT_CREATE_WELCOME } from '@/stores/templateChatStore'
import { chatTemplateEdit, applyChatTemplateEdit } from '@/api/client'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { useToast } from '@/components/ToastProvider'

const MODE_CONFIG = {
  edit: {
    welcomeMessage: null,
    placeholder: 'Describe the changes you want...',
    sendLabel: 'Generate edit suggestions',
  },
  create: {
    welcomeMessage: DEFAULT_CREATE_WELCOME,
    placeholder: 'Describe the report template you need...',
    sendLabel: 'Generate template',
  },
}

export { MODE_CONFIG }

export function useTemplateChatEditor({
  templateId,
  templateName,
  currentHtml,
  onHtmlUpdate,
  onApplySuccess,
  onRequestSave,
  mode = 'edit',
  chatApi = null,
}) {
  const modeConfig = MODE_CONFIG[mode] || MODE_CONFIG.edit
  const chatApiFunction = chatApi || ((messages, html) => chatTemplateEdit(templateId, messages, html))
  const toast = useToast()
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const [inputValue, setInputValue] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [applying, setApplying] = useState(false)
  const [followUpQuestions, setFollowUpQuestions] = useState(null)

  // Get store methods
  const getOrCreateSession = useTemplateChatStore((s) => s.getOrCreateSession)
  const getSession = useTemplateChatStore((s) => s.getSession)
  const addUserMessage = useTemplateChatStore((s) => s.addUserMessage)
  const addAssistantMessage = useTemplateChatStore((s) => s.addAssistantMessage)
  const getMessagesForApi = useTemplateChatStore((s) => s.getMessagesForApi)
  const setProposedChanges = useTemplateChatStore((s) => s.setProposedChanges)
  const clearProposedChanges = useTemplateChatStore((s) => s.clearProposedChanges)
  const clearSession = useTemplateChatStore((s) => s.clearSession)
  const { execute } = useInteraction()

  // Initialize session
  useEffect(() => {
    if (templateId) {
      getOrCreateSession(templateId, templateName, modeConfig.welcomeMessage)
    }
  }, [templateId, templateName, getOrCreateSession, modeConfig.welcomeMessage])

  const session = getSession(templateId)
  const messages = session?.messages || []
  const proposedChanges = session?.proposedChanges
  const proposedHtml = session?.proposedHtml
  const readyToApply = session?.readyToApply

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSendMessage = useCallback(async () => {
    const text = inputValue.trim()
    if (!text || isProcessing || !templateId) return

    setInputValue('')
    setFollowUpQuestions(null)
    addUserMessage(templateId, text)

    await execute({
      type: InteractionType.GENERATE,
      label: modeConfig.sendLabel,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId,
        action: mode === 'create' ? 'template_chat_create' : 'template_chat',
      },
      action: async () => {
        setIsProcessing(true)
        try {
          const apiMessages = getMessagesForApi(templateId)
          const response = await chatApiFunction(apiMessages, currentHtml)

          addAssistantMessage(templateId, response.message, {
            proposedChanges: response.proposed_changes,
            proposedHtml: response.updated_html,
            readyToApply: response.ready_to_apply,
          })

          setProposedChanges(templateId, {
            proposedChanges: response.proposed_changes,
            proposedHtml: response.updated_html,
            readyToApply: response.ready_to_apply,
          })

          if (mode === 'create' && response.updated_html) {
            onHtmlUpdate?.(response.updated_html)
          }

          if (response.follow_up_questions) {
            setFollowUpQuestions(response.follow_up_questions)
          }
          return response
        } catch (err) {
          toast.show(String(err.message || err), 'error')
          addAssistantMessage(
            templateId,
            "I apologize, but I encountered an error. Please try again or rephrase your request."
          )
          throw err
        } finally {
          setIsProcessing(false)
        }
      },
    })
  }, [
    inputValue,
    isProcessing,
    templateId,
    currentHtml,
    addUserMessage,
    addAssistantMessage,
    getMessagesForApi,
    setProposedChanges,
    toast,
    execute,
    chatApiFunction,
    mode,
    modeConfig.sendLabel,
  ])

  const handleApplyChanges = useCallback(async () => {
    if (!proposedHtml || !templateId) return

    await execute({
      type: InteractionType.UPDATE,
      label: 'Apply template changes',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId,
        action: 'apply_template_changes',
      },
      action: async () => {
        setApplying(true)
        try {
          let result
          if (mode === 'create') {
            result = { updated_html: proposedHtml }
          } else {
            result = await applyChatTemplateEdit(templateId, proposedHtml)
          }

          clearProposedChanges(templateId)
          onHtmlUpdate?.(proposedHtml)
          onApplySuccess?.(result)

          if (mode === 'create') {
            addAssistantMessage(
              templateId,
              "Your template is ready! Opening the save dialog so you can name and save it."
            )
          } else {
            addAssistantMessage(
              templateId,
              "The changes have been applied successfully. Is there anything else you'd like to modify?"
            )
          }

          toast.show('Template changes applied successfully.', 'success')

          if (mode === 'create' && onRequestSave) {
            onRequestSave()
          }

          return result
        } catch (err) {
          toast.show(String(err.message || err), 'error')
          throw err
        } finally {
          setApplying(false)
        }
      },
    })
  }, [
    proposedHtml,
    templateId,
    mode,
    clearProposedChanges,
    addAssistantMessage,
    onHtmlUpdate,
    onApplySuccess,
    onRequestSave,
    toast,
    execute,
  ])

  const handleRejectChanges = useCallback(() => {
    clearProposedChanges(templateId)
    addAssistantMessage(
      templateId,
      "No problem! What different changes would you like me to make instead?"
    )
  }, [templateId, clearProposedChanges, addAssistantMessage])

  const handleQuestionClick = useCallback((question) => {
    setInputValue(question)
    setFollowUpQuestions(null)
    inputRef.current?.focus()
  }, [])

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSendMessage()
      }
    },
    [handleSendMessage]
  )

  const handleClearChat = useCallback(() => {
    clearSession(templateId, templateName, modeConfig.welcomeMessage)
    setFollowUpQuestions(null)
    if (mode === 'create') {
      onHtmlUpdate?.('')
    }
    toast.show('Chat cleared. Starting fresh conversation.', 'info')
  }, [templateId, templateName, clearSession, toast, modeConfig.welcomeMessage, mode, onHtmlUpdate])

  return {
    // Refs
    messagesEndRef,
    inputRef,
    // State
    inputValue,
    setInputValue,
    isProcessing,
    applying,
    followUpQuestions,
    // Session data
    messages,
    proposedChanges,
    proposedHtml,
    readyToApply,
    // Config
    modeConfig,
    // Handlers
    handleSendMessage,
    handleApplyChanges,
    handleRejectChanges,
    handleQuestionClick,
    handleKeyDown,
    handleClearChat,
  }
}
