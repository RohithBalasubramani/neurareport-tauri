import { useState, useRef, useCallback, useEffect } from 'react'
import {
  Box,
  Stack,
  Typography,
  Button,
  TextField,
  CircularProgress,
  Paper,
  Chip,
  IconButton,
  Divider,
  Alert,
  Collapse,
  alpha,
  Autocomplete,
  Table,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import RefreshIcon from '@mui/icons-material/Refresh'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import PersonOutlineIcon from '@mui/icons-material/PersonOutline'
import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import QueueIcon from '@mui/icons-material/Queue'
import LinearProgress from '@mui/material/LinearProgress'

import { useTemplateChatStore, DEFAULT_CREATE_WELCOME } from '@/stores/templateChatStore'
import { chatTemplateEdit, applyChatTemplateEdit } from '@/api/client'

const MODE_CONFIG = {
  edit: {
    welcomeMessage: null, // uses default edit welcome
    placeholder: 'Describe the changes you want...',
    sendLabel: 'Generate edit suggestions',
  },
  create: {
    welcomeMessage: DEFAULT_CREATE_WELCOME,
    placeholder: 'Describe the report template you need...',
    sendLabel: 'Generate template',
  },
}
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { useToast } from '@/components/ToastProvider'
import ScaledIframePreview from '@/components/ScaledIframePreview'
import { neutral, palette } from '@/app/theme'

const ROLE_CONFIG = {
  user: {
    icon: PersonOutlineIcon,
    label: 'You',
    bgcolor: neutral[900],
    textColor: 'common.white',
  },
  assistant: {
    icon: SmartToyOutlinedIcon,
    label: 'NeuraReport',
    bgcolor: 'background.paper',
    textColor: 'text.primary',
  },
}

function ChatMessage({ message }) {
  const { role, content, timestamp } = message
  const config = ROLE_CONFIG[role] || ROLE_CONFIG.assistant
  const Icon = config.icon
  const isUser = role === 'user'

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: 1.5,
        px: 2,
        py: 1.5,
      }}
    >
      <Box
        sx={{
          width: 32,
          height: 32,
          borderRadius: '50%',
          bgcolor: isUser ? neutral[900] : neutral[500],
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <Icon sx={{ fontSize: 18, color: 'white' }} />
      </Box>

      <Box
        sx={{
          flex: 1,
          maxWidth: isUser ? 'calc(100% - 100px)' : 'calc(100% - 48px)',
          minWidth: 0,
        }}
      >
        <Stack
          direction="row"
          spacing={1}
          alignItems="center"
          sx={{
            mb: 0.5,
            justifyContent: isUser ? 'flex-end' : 'flex-start',
          }}
        >
          <Typography variant="caption" fontWeight={600} color="text.primary">
            {config.label}
          </Typography>
          {timestamp && (
            <Typography variant="caption" color="text.disabled">
              {new Date(timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Typography>
          )}
        </Stack>

        <Box
          sx={{
            p: 2,
            borderRadius: 1,  // Figma spec: 8px
            bgcolor: isUser
              ? neutral[900]
              : 'background.paper',
            color: isUser ? 'common.white' : 'text.primary',
            boxShadow: isUser
              ? `0 2px 8px ${alpha(neutral[900], 0.2)}`
              : '0 1px 3px rgba(0,0,0,0.08)',
          }}
        >
          <Typography
            variant="body2"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              lineHeight: 1.6,
            }}
          >
            {content}
            {message.streaming && (
              <Box
                component="span"
                sx={{
                  display: 'inline-block',
                  width: 6,
                  height: 16,
                  ml: 0.5,
                  bgcolor: 'currentColor',
                  animation: 'blink 1s steps(1) infinite',
                  '@keyframes blink': {
                    '50%': { opacity: 0 },
                  },
                }}
              />
            )}
          </Typography>
        </Box>
      </Box>
    </Box>
  )
}

function ProposedChangesPanel({ changes, proposedHtml, onApply, onReject, applying }) {
  const [showPreview, setShowPreview] = useState(false)
  const [previewUrl, setPreviewUrl] = useState(null)

  useEffect(() => {
    if (!proposedHtml) {
      setPreviewUrl(null)
      return
    }
    const blob = new Blob([proposedHtml], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    setPreviewUrl(url)
    return () => {
      URL.revokeObjectURL(url)
    }
  }, [proposedHtml])

  if (!changes || changes.length === 0) return null

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        mx: 2,
        mb: 2,
        borderRadius: 1,  // Figma spec: 8px
        border: '1px solid',
        borderColor: (theme) => alpha(theme.palette.divider, 0.3),
        bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
      }}
    >
      <Stack spacing={2}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <CheckCircleIcon sx={{ color: 'text.secondary' }} fontSize="small" />
          <Typography variant="subtitle2" fontWeight={600}>
            Ready to Apply Changes
          </Typography>
        </Stack>

        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Proposed modifications:
          </Typography>
          <Stack spacing={0.5}>
            {changes.map((change, idx) => (
              <Stack key={idx} direction="row" spacing={1} alignItems="flex-start">
                <Typography variant="body2" color="text.secondary">
                  •
                </Typography>
                <Typography variant="body2">
                  {change}
                </Typography>
              </Stack>
            ))}
          </Stack>
        </Box>

        {proposedHtml && (
          <Box>
            <Button
              size="small"
              variant="text"
              onClick={() => setShowPreview(!showPreview)}
              endIcon={showPreview ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{ mb: 1 }}
            >
              {showPreview ? 'Hide Preview' : 'Show Preview'}
            </Button>
            <Collapse in={showPreview}>
              <Box
                sx={{
                  borderRadius: 1,  // Figma spec: 8px
                  border: '1px solid',
                  borderColor: 'divider',
                  bgcolor: 'background.paper',
                  p: 1,
                  height: 300,
                  overflow: 'hidden',
                }}
              >
                {previewUrl && (
                  <ScaledIframePreview
                    src={previewUrl}
                    title="Proposed changes preview"
                    fit="contain"
                    pageShadow
                    frameAspectRatio="210 / 297"
                  />
                )}
              </Box>
            </Collapse>
          </Box>
        )}

        <Stack direction="row" spacing={1.5}>
          <Button
            variant="contained"
            onClick={onApply}
            disabled={applying}
            startIcon={applying ? <CircularProgress size={16} /> : <CheckCircleIcon />}
          >
            {applying ? 'Applying...' : 'Apply Changes'}
          </Button>
          <Button
            variant="outlined"
            color="inherit"
            onClick={onReject}
            disabled={applying}
          >
            Request Different Changes
          </Button>
        </Stack>
      </Stack>
    </Paper>
  )
}

function FollowUpQuestions({ questions, onQuestionClick }) {
  if (!questions || questions.length === 0) return null

  return (
    <Box sx={{ px: 2, pb: 1.5 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <LightbulbIcon fontSize="small" color="action" />
        <Typography variant="caption" color="text.secondary">
          Quick responses:
        </Typography>
      </Stack>
      <Stack direction="row" flexWrap="wrap" gap={1}>
        {questions.map((question, idx) => (
          <Chip
            key={idx}
            label={question}
            size="small"
            variant="outlined"
            onClick={() => onQuestionClick(question)}
            sx={{
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          />
        ))}
      </Stack>
    </Box>
  )
}

const SPECIAL_VALUES = new Set(['UNRESOLVED', 'INPUT_SAMPLE', 'LATER_SELECTED'])

function humanizeToken(token) {
  return token.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function humanizeColumn(col) {
  if (!col || SPECIAL_VALUES.has(col)) return null
  // "table.column" → "Column (from Table)"
  const parts = col.split('.')
  if (parts.length === 2) {
    const table = parts[0].replace(/_/g, ' ')
    const column = parts[1].replace(/_/g, ' ')
    return `${column} from ${table}`
  }
  return col.replace(/_/g, ' ')
}

const PROGRESS_STEPS = [
  'Preparing mapping...',
  'Building contract...',
  'Generating report assets...',
  'Finalizing template...',
]

function MappingReviewPanel({ mappingData, catalog, schemaInfo, onApprove, onSkip, onQueue, approving }) {
  const [localMapping, setLocalMapping] = useState(() => ({ ...(mappingData || {}) }))
  const [showDetails, setShowDetails] = useState(false)
  const [editingToken, setEditingToken] = useState(null)
  const [progressStep, setProgressStep] = useState(0)

  const catalogOptions = (catalog || []).map((c) => c)

  const handleChange = (token, newValue) => {
    setLocalMapping((prev) => ({ ...prev, [token]: newValue || '' }))
  }

  // Cycle through progress steps while approving
  useEffect(() => {
    if (!approving) { setProgressStep(0); return }
    const timer = setInterval(() => {
      setProgressStep((prev) => (prev + 1) % PROGRESS_STEPS.length)
    }, 3000)
    return () => clearInterval(timer)
  }, [approving])

  const tokens = Object.keys(localMapping)
  const mapped = tokens.filter((t) => !SPECIAL_VALUES.has(localMapping[t]) && localMapping[t])
  const unresolved = tokens.filter((t) => SPECIAL_VALUES.has(localMapping[t]) || !localMapping[t])

  const tables = schemaInfo
    ? [schemaInfo['child table'], schemaInfo['parent table']].filter(Boolean).join(' and ')
    : null

  // --- Processing state: rolling progress ---
  if (approving) {
    return (
      <Paper
        elevation={0}
        sx={{
          p: 2.5,
          mx: 2,
          mb: 2,
          borderRadius: 1,
          border: '1px solid',
          borderColor: (theme) => alpha(theme.palette.primary.main, 0.3),
          bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.primary.main, 0.08) : alpha(theme.palette.primary.main, 0.04),
        }}
      >
        <Stack spacing={2} alignItems="center">
          <Stack direction="row" spacing={1.5} alignItems="center">
            <CircularProgress size={22} thickness={5} />
            <Typography variant="subtitle2" fontWeight={600}>
              Setting up your template...
            </Typography>
          </Stack>

          <Box sx={{ width: '100%' }}>
            <LinearProgress
              variant="indeterminate"
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: (theme) => alpha(theme.palette.primary.main, 0.12),
                '& .MuiLinearProgress-bar': { borderRadius: 3 },
              }}
            />
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ minHeight: 20, transition: 'opacity 0.3s' }}>
            {PROGRESS_STEPS[progressStep]}
          </Typography>

          {onQueue && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<QueueIcon />}
              onClick={onQueue}
              sx={{ textTransform: 'none', mt: 0.5 }}
            >
              Queue & Continue — I'll finish this in the background
            </Button>
          )}
        </Stack>
      </Paper>
    )
  }

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        mx: 2,
        mb: 2,
        borderRadius: 1,
        border: '1px solid',
        borderColor: (theme) => alpha(theme.palette.divider, 0.3),
        bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
      }}
    >
      <Stack spacing={1.5}>
        {/* Friendly summary */}
        <Typography variant="body2" sx={{ lineHeight: 1.7 }}>
          {tables && <>I found your data in the <strong>{tables}</strong> table{tables.includes(' and ') ? 's' : ''}. </>}
          {mapped.length > 0 && (
            <>I was able to connect <strong>{mapped.length} of {tokens.length}</strong> template fields to your database. </>
          )}
          {unresolved.length > 0 && (
            <>{mapped.length > 0 ? 'However, ' : ''}<strong>{unresolved.length} field{unresolved.length > 1 ? 's' : ''}</strong> still need{unresolved.length === 1 ? 's' : ''} to be configured.</>
          )}
          {unresolved.length === 0 && mapped.length > 0 && (
            <>All fields are mapped and ready to go!</>
          )}
        </Typography>

        {/* Mapped fields — compact list */}
        {mapped.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 0.5, display: 'block' }}>
              Connected fields:
            </Typography>
            <Stack direction="row" flexWrap="wrap" gap={0.5}>
              {mapped.map((token) => (
                <Chip
                  key={token}
                  label={`${humanizeToken(token)} → ${humanizeColumn(localMapping[token]) || localMapping[token]}`}
                  size="small"
                  variant="outlined"
                  color="success"
                  sx={{ fontSize: '0.7rem' }}
                />
              ))}
            </Stack>
          </Box>
        )}

        {/* Unresolved fields — highlighted */}
        {unresolved.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 0.5, display: 'block' }}>
              Needs your input:
            </Typography>
            <Stack spacing={0.5}>
              {unresolved.map((token) => (
                <Stack key={token} direction="row" alignItems="center" spacing={1}>
                  <Typography variant="body2" sx={{ minWidth: 120 }}>
                    {humanizeToken(token)}
                  </Typography>
                  {editingToken === token ? (
                    <Autocomplete
                      freeSolo
                      size="small"
                      options={catalogOptions}
                      value={localMapping[token] || ''}
                      onChange={(_e, newVal) => {
                        handleChange(token, newVal)
                        setEditingToken(null)
                      }}
                      onBlur={() => setEditingToken(null)}
                      renderInput={(params) => (
                        <TextField {...params} variant="outlined" autoFocus size="small" placeholder="Pick a column..."
                          sx={{ '& .MuiInputBase-root': { fontSize: '0.8rem', py: 0 } }}
                        />
                      )}
                      sx={{ flex: 1, minWidth: 150 }}
                    />
                  ) : (
                    <Chip
                      label="Select column..."
                      size="small"
                      color="warning"
                      variant="outlined"
                      onClick={() => setEditingToken(token)}
                      sx={{ cursor: 'pointer', fontSize: '0.75rem' }}
                    />
                  )}
                </Stack>
              ))}
            </Stack>
          </Box>
        )}

        {/* Expandable detail view */}
        {mapped.length > 0 && (
          <Button
            size="small"
            variant="text"
            onClick={() => setShowDetails(!showDetails)}
            endIcon={showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            sx={{ alignSelf: 'flex-start', textTransform: 'none', fontSize: '0.75rem' }}
          >
            {showDetails ? 'Hide all mappings' : 'View all mappings'}
          </Button>
        )}

        <Collapse in={showDetails}>
          <Box sx={{ maxHeight: 250, overflow: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 0.5 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600, bgcolor: 'background.paper', width: '40%', py: 0.5 }}>Field</TableCell>
                  <TableCell sx={{ fontWeight: 600, bgcolor: 'background.paper', py: 0.5 }}>Source</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tokens.map((token) => {
                  const value = localMapping[token]
                  const isSpecial = SPECIAL_VALUES.has(value) || !value
                  return (
                    <TableRow key={token} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                      <TableCell sx={{ py: 0.5 }}>
                        <Typography variant="body2" fontSize="0.8rem">{humanizeToken(token)}</Typography>
                      </TableCell>
                      <TableCell sx={{ py: 0.5 }}>
                        {editingToken === token ? (
                          <Autocomplete
                            freeSolo
                            size="small"
                            options={catalogOptions}
                            value={value || ''}
                            onChange={(_e, newVal) => { handleChange(token, newVal); setEditingToken(null) }}
                            onBlur={() => setEditingToken(null)}
                            renderInput={(params) => (
                              <TextField {...params} variant="outlined" autoFocus size="small"
                                sx={{ '& .MuiInputBase-root': { fontSize: '0.8rem', py: 0 } }}
                              />
                            )}
                            sx={{ minWidth: 150 }}
                          />
                        ) : (
                          <Chip
                            label={isSpecial ? 'Not set' : (humanizeColumn(value) || value)}
                            size="small"
                            color={isSpecial ? 'warning' : 'default'}
                            variant="outlined"
                            onClick={() => setEditingToken(token)}
                            sx={{ cursor: 'pointer', fontSize: '0.7rem' }}
                          />
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </Box>
        </Collapse>

        <Typography variant="body2" color="text.secondary" fontSize="0.8rem">
          Looks good? Approve to finalize, or tell me what you'd like to change.
        </Typography>

        <Stack direction="row" spacing={1.5}>
          <Button
            variant="contained"
            onClick={() => onApprove(localMapping)}
            disabled={approving}
            startIcon={<CheckCircleIcon />}
            sx={{ textTransform: 'none' }}
          >
            Looks Good, Approve
          </Button>
          <Button
            variant="outlined"
            onClick={() => onApprove(mappingData)}
            disabled={approving}
            sx={{ textTransform: 'none' }}
          >
            You do this
          </Button>
        </Stack>
      </Stack>
    </Paper>
  )
}

export default function TemplateChatEditor({
  templateId,
  templateName,
  currentHtml,
  onHtmlUpdate,
  onApplySuccess,
  onRequestSave,
  onMappingApprove,
  onMappingSkip,
  onMappingQueue,
  mappingPreviewData,
  mappingApproving = false,
  mode = 'edit',
  chatApi = null,
}) {
  const modeConfig = MODE_CONFIG[mode] || MODE_CONFIG.edit
  // In edit mode, bind templateId into the API call; in create mode, use the provided chatApi
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
          // Get messages for API (already includes the user message added above)
          const apiMessages = getMessagesForApi(templateId)

          const response = await chatApiFunction(apiMessages, currentHtml)

          // Add assistant response
          addAssistantMessage(templateId, response.message, {
            proposedChanges: response.proposed_changes,
            proposedHtml: response.updated_html,
            readyToApply: response.ready_to_apply,
          })

          // Update proposed changes state
          setProposedChanges(templateId, {
            proposedChanges: response.proposed_changes,
            proposedHtml: response.updated_html,
            readyToApply: response.ready_to_apply,
          })

          // In create mode, update the live preview as soon as the AI
          // produces HTML so the left-hand side stays in sync.
          if (mode === 'create' && response.updated_html) {
            onHtmlUpdate?.(response.updated_html)
          }

          // Set follow-up questions if provided
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
            // In create mode the template doesn't exist on disk yet —
            // just update local state without hitting the backend.
            result = { updated_html: proposedHtml }
          } else {
            result = await applyChatTemplateEdit(templateId, proposedHtml)
          }

          // Clear proposed changes
          clearProposedChanges(templateId)

          // Notify parent of HTML update
          onHtmlUpdate?.(proposedHtml)
          onApplySuccess?.(result)

          // Add confirmation message
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

          // In create mode, auto-open the save dialog
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
    // In create mode, also clear the parent's HTML so preview resets
    if (mode === 'create') {
      onHtmlUpdate?.('')
    }
    toast.show('Chat cleared. Starting fresh conversation.', 'info')
  }, [templateId, templateName, clearSession, toast, modeConfig.welcomeMessage, mode, onHtmlUpdate])

  return (
    <Box
      sx={{
        height: '100%',
        minHeight: 0,         /* respect grid cell constraint */
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
        borderRadius: 1,  // Figma spec: 8px
        border: '1px solid',
        borderColor: 'divider',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: 'background.paper',
        }}
      >
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              {mode === 'create' ? 'AI Template Creator' : 'AI Template Editor'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {mode === 'create'
                ? 'Describe the report you need and I\'ll build it for you'
                : 'Describe the changes you want and I\'ll help you implement them'}
            </Typography>
          </Box>
          <IconButton
            size="small"
            onClick={handleClearChat}
            title="Clear chat and start over"
          >
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Stack>
      </Box>

      {/* Messages + Proposed Changes + Follow-ups — all in one scrollable area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          py: 1,
          minHeight: 0,
        }}
      >
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Proposed Changes Panel */}
        {readyToApply && proposedChanges && (
          <ProposedChangesPanel
            changes={proposedChanges}
            proposedHtml={proposedHtml}
            onApply={handleApplyChanges}
            onReject={handleRejectChanges}
            applying={applying}
          />
        )}

        {/* Mapping Review Panel — shown after template save in create mode */}
        {mappingPreviewData && onMappingApprove && (
          <MappingReviewPanel
            mappingData={mappingPreviewData.mapping}
            catalog={mappingPreviewData.catalog}
            schemaInfo={mappingPreviewData.schema_info}
            onApprove={onMappingApprove}
            onSkip={onMappingSkip}
            onQueue={onMappingQueue}
            approving={mappingApproving}
          />
        )}

        {/* Follow-up Questions */}
        <FollowUpQuestions
          questions={followUpQuestions}
          onQuestionClick={handleQuestionClick}
        />

        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box
        sx={{
          p: 2,
          borderTop: '1px solid',
          borderColor: 'divider',
          bgcolor: 'background.paper',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            gap: 1,
            p: 1.5,
            borderRadius: 1,  // Figma spec: 8px
            bgcolor: (theme) => alpha(theme.palette.action.hover, 0.5),
            border: 1,
            borderColor: 'divider',
            transition: 'all 150ms cubic-bezier(0.22, 1, 0.36, 1)',
            '&:focus-within': {
              borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
              boxShadow: (theme) =>
                `0 0 0 2px ${alpha(theme.palette.text.primary, 0.08)}`,
            },
          }}
        >
          <TextField
            inputRef={inputRef}
            fullWidth
            multiline
            maxRows={4}
            placeholder={
              isProcessing
                ? 'Processing...'
                : readyToApply
                ? 'Apply the changes above or describe different modifications...'
                : modeConfig.placeholder
            }
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isProcessing}
            variant="standard"
            InputProps={{
              disableUnderline: true,
              sx: {
                fontSize: '1rem',
                lineHeight: 1.5,
              },
            }}
            sx={{
              '& .MuiInputBase-root': {
                py: 0.5,
              },
            }}
          />

          <IconButton
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isProcessing}
            sx={{
              bgcolor: (theme) => inputValue.trim() && !isProcessing
                ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
                : 'action.disabledBackground',
              color: inputValue.trim() && !isProcessing
                ? 'common.white'
                : 'text.disabled',
              '&:hover': {
                bgcolor: (theme) => inputValue.trim() && !isProcessing
                  ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
                  : 'action.disabledBackground',
              },
            }}
          >
            {isProcessing ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              <SendIcon fontSize="small" />
            )}
          </IconButton>
        </Box>

        <Stack
          direction="row"
          spacing={2}
          justifyContent="center"
          sx={{ mt: 1 }}
        >
          <Typography variant="caption" color="text.disabled">
            Press Enter to send, Shift+Enter for new line
          </Typography>
        </Stack>
      </Box>
    </Box>
  )
}
