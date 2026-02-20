import { create } from 'zustand'
import { nanoid } from 'nanoid'

/**
 * Store for managing template editing chat sessions.
 * Each template can have its own chat session with conversation history.
 */

const createMessage = (role, content, metadata = {}) => ({
  id: nanoid(),
  role, // 'user' | 'assistant' | 'system'
  content,
  timestamp: Date.now(),
  streaming: false,
  ...metadata,
})

const DEFAULT_EDIT_WELCOME = "I've reviewed your template. What changes would you like to make? Feel free to describe what you want - whether it's styling updates, layout changes, adding or removing sections, or any other modifications."

const DEFAULT_CREATE_WELCOME = "I'll help you create a report template from scratch. What kind of report do you need? For example: invoice, sales summary, inventory report, financial statement, or something else?"

const createChatSession = (templateId, templateName, welcomeMessage) => ({
  id: nanoid(),
  templateId,
  templateName,
  messages: [
    createMessage('assistant', welcomeMessage || DEFAULT_EDIT_WELCOME),
  ],
  createdAt: Date.now(),
  updatedAt: Date.now(),
  // Track the proposed changes state
  proposedChanges: null,
  proposedHtml: null,
  readyToApply: false,
})

export const useTemplateChatStore = create((set, get) => ({
  // Map of templateId -> chat session
  sessions: {},

  // Get or create a session for a template
  getOrCreateSession: (templateId, templateName = 'Template', welcomeMessage = null) => {
    const { sessions } = get()
    if (sessions[templateId]) {
      return sessions[templateId]
    }
    const session = createChatSession(templateId, templateName, welcomeMessage)
    set((state) => ({
      sessions: {
        ...state.sessions,
        [templateId]: session,
      },
    }))
    return session
  },

  // Get session for a template (returns null if not exists)
  getSession: (templateId) => {
    return get().sessions[templateId] || null
  },

  // Add a user message to the session
  addUserMessage: (templateId, content) => {
    const message = createMessage('user', content)
    set((state) => {
      const session = state.sessions[templateId]
      if (!session) return state
      return {
        sessions: {
          ...state.sessions,
          [templateId]: {
            ...session,
            messages: [...session.messages, message].slice(-500),
            updatedAt: Date.now(),
          },
        },
      }
    })
    return message.id
  },

  // Add an assistant message to the session
  addAssistantMessage: (templateId, content, metadata = {}) => {
    const message = createMessage('assistant', content, metadata)
    set((state) => {
      const session = state.sessions[templateId]
      if (!session) return state
      return {
        sessions: {
          ...state.sessions,
          [templateId]: {
            ...session,
            messages: [...session.messages, message].slice(-500),
            updatedAt: Date.now(),
            // Update proposed changes if provided
            ...(metadata.proposedChanges !== undefined && {
              proposedChanges: metadata.proposedChanges,
            }),
            ...(metadata.proposedHtml !== undefined && {
              proposedHtml: metadata.proposedHtml,
            }),
            ...(metadata.readyToApply !== undefined && {
              readyToApply: metadata.readyToApply,
            }),
          },
        },
      }
    })
    return message.id
  },

  // Add a streaming assistant message (initially empty)
  addStreamingMessage: (templateId) => {
    const message = createMessage('assistant', '', { streaming: true })
    set((state) => {
      const session = state.sessions[templateId]
      if (!session) return state
      return {
        sessions: {
          ...state.sessions,
          [templateId]: {
            ...session,
            messages: [...session.messages, message].slice(-500),
            updatedAt: Date.now(),
          },
        },
      }
    })
    return message.id
  },

  // Update a message content (for streaming)
  updateMessageContent: (templateId, messageId, content) => {
    set((state) => {
      const session = state.sessions[templateId]
      if (!session) return state
      return {
        sessions: {
          ...state.sessions,
          [templateId]: {
            ...session,
            messages: session.messages.map((m) =>
              m.id === messageId ? { ...m, content } : m
            ),
          },
        },
      }
    })
  },

  // Append to a message content (for streaming)
  appendToMessage: (templateId, messageId, content) => {
    set((state) => {
      const session = state.sessions[templateId]
      if (!session) return state
      return {
        sessions: {
          ...state.sessions,
          [templateId]: {
            ...session,
            messages: session.messages.map((m) =>
              m.id === messageId ? { ...m, content: m.content + content } : m
            ),
          },
        },
      }
    })
  },

  // Mark a message as done streaming
  finishStreaming: (templateId, messageId, metadata = {}) => {
    set((state) => {
      const session = state.sessions[templateId]
      if (!session) return state
      return {
        sessions: {
          ...state.sessions,
          [templateId]: {
            ...session,
            messages: session.messages.map((m) =>
              m.id === messageId ? { ...m, streaming: false, ...metadata } : m
            ),
            // Update proposed changes if provided
            ...(metadata.proposedChanges !== undefined && {
              proposedChanges: metadata.proposedChanges,
            }),
            ...(metadata.proposedHtml !== undefined && {
              proposedHtml: metadata.proposedHtml,
            }),
            ...(metadata.readyToApply !== undefined && {
              readyToApply: metadata.readyToApply,
            }),
          },
        },
      }
    })
  },

  // Update proposed changes state
  setProposedChanges: (templateId, { proposedChanges, proposedHtml, readyToApply }) => {
    set((state) => {
      const session = state.sessions[templateId]
      if (!session) return state
      return {
        sessions: {
          ...state.sessions,
          [templateId]: {
            ...session,
            proposedChanges: proposedChanges ?? session.proposedChanges,
            proposedHtml: proposedHtml ?? session.proposedHtml,
            readyToApply: readyToApply ?? session.readyToApply,
          },
        },
      }
    })
  },

  // Clear proposed changes after applying
  clearProposedChanges: (templateId) => {
    set((state) => {
      const session = state.sessions[templateId]
      if (!session) return state
      return {
        sessions: {
          ...state.sessions,
          [templateId]: {
            ...session,
            proposedChanges: null,
            proposedHtml: null,
            readyToApply: false,
          },
        },
      }
    })
  },

  // Clear a session (start fresh conversation)
  clearSession: (templateId, templateName, welcomeMessage = null) => {
    const session = createChatSession(templateId, templateName, welcomeMessage)
    set((state) => ({
      sessions: {
        ...state.sessions,
        [templateId]: session,
      },
    }))
    return session
  },

  // Delete a session entirely
  deleteSession: (templateId) => {
    set((state) => {
      const { [templateId]: removed, ...rest } = state.sessions
      return { sessions: rest }
    })
  },

  // Get messages for a template in the format needed for the API
  getMessagesForApi: (templateId) => {
    const session = get().sessions[templateId]
    if (!session) return []
    // Filter out system messages and convert to API format
    return session.messages
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map((m) => ({
        role: m.role,
        content: m.content,
      }))
  },
}))

export { DEFAULT_EDIT_WELCOME, DEFAULT_CREATE_WELCOME }
export default useTemplateChatStore
