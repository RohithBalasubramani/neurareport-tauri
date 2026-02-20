/**
 * Agents API Client v2
 * Production-grade client for AI agent operations with:
 * - Persistent task storage
 * - Idempotency support
 * - Progress tracking
 * - Task management (cancel, retry)
 *
 * Usage:
 *   import { runResearchAgent, pollTaskUntilComplete, cancelTask } from './agentsV2';
 *
 *   // Async execution with polling
 *   const task = await runResearchAgent('AI trends', { sync: false });
 *   const result = await pollTaskUntilComplete(task.task_id, {
 *     onProgress: (task) => console.log(`${task.progress.percent}%`)
 *   });
 *
 *   // Sync execution (waits for completion)
 *   const result = await runResearchAgent('AI trends', { sync: true });
 */
import { api, toApiUrl } from './client';

const BASE_PATH = '/agents/v2';

const asArray = (payload, keys = []) => {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
};

// ============================================
// Error Types
// ============================================

export class AgentError extends Error {
  constructor(code, message, retryable = false, details = {}) {
    super(message);
    this.name = 'AgentError';
    this.code = code;
    this.retryable = retryable;
    this.details = details;
  }
}

export class ValidationError extends AgentError {
  constructor(message, field = null) {
    super('VALIDATION_ERROR', message, false, { field });
    this.name = 'ValidationError';
  }
}

export class TaskNotFoundError extends AgentError {
  constructor(taskId) {
    super('TASK_NOT_FOUND', `Task ${taskId} not found`, false, { taskId });
    this.name = 'TaskNotFoundError';
  }
}

export class TaskConflictError extends AgentError {
  constructor(message) {
    super('TASK_CONFLICT', message, false);
    this.name = 'TaskConflictError';
  }
}

// ============================================
// Response Helpers
// ============================================

function handleApiError(error) {
  if (error.response) {
    const { status, data } = error.response;
    const detail = data?.detail || {};

    if (status === 400) {
      throw new ValidationError(detail.message || 'Invalid request', detail.field);
    }
    if (status === 404) {
      throw new TaskNotFoundError(detail.taskId || 'unknown');
    }
    if (status === 409) {
      throw new TaskConflictError(detail.message || 'Task conflict');
    }
    if (status === 429) {
      throw new AgentError(
        'RATE_LIMITED',
        detail.message || 'Rate limit exceeded',
        true,
        { retryAfter: detail.retry_after || 60 }
      );
    }

    throw new AgentError(
      detail.code || 'API_ERROR',
      detail.message || error.message,
      detail.retryable ?? true
    );
  }

  throw new AgentError('NETWORK_ERROR', error.message, true);
}

// ============================================
// Research Agent
// ============================================

/**
 * Run the research agent to compile a comprehensive report on a topic.
 *
 * @param {string} topic - Topic to research (at least 2 words)
 * @param {Object} options - Configuration options
 * @param {string} options.depth - Research depth: 'quick', 'moderate', 'comprehensive' (default)
 * @param {string[]} options.focusAreas - Specific areas to focus on (max 10)
 * @param {number} options.maxSections - Maximum sections in report (1-20, default 5)
 * @param {string} options.idempotencyKey - Unique key for deduplication
 * @param {number} options.priority - Task priority (0-10, default 0)
 * @param {string} options.webhookUrl - URL to notify on completion
 * @param {boolean} options.sync - Wait for completion (default true)
 * @returns {Promise<Object>} Task response with status, progress, and result
 */
export async function runResearchAgent(topic, options = {}) {
  try {
    const response = await api.post(`${BASE_PATH}/research`, {
      topic,
      depth: options.depth || 'comprehensive',
      focus_areas: options.focusAreas || null,
      max_sections: options.maxSections || 5,
      idempotency_key: options.idempotencyKey || null,
      priority: options.priority || 0,
      webhook_url: options.webhookUrl || null,
      sync: options.sync !== false, // Default to true
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================
// Data Analyst Agent
// ============================================

/**
 * Run the data analyst agent to analyse tabular data.
 *
 * @param {string} question - Question to answer about the data
 * @param {Object[]} data - Tabular data as array of objects
 * @param {Object} options - Configuration options
 * @param {string} options.dataDescription - Optional description of the dataset
 * @param {boolean} options.generateCharts - Whether to suggest charts (default true)
 * @param {string} options.idempotencyKey - Unique key for deduplication
 * @param {number} options.priority - Task priority (0-10)
 * @param {string} options.webhookUrl - Webhook URL for completion
 * @param {boolean} options.sync - Wait for completion (default true)
 * @returns {Promise<Object>} Task response
 */
export async function runDataAnalystAgent(question, data, options = {}) {
  try {
    const response = await api.post(`${BASE_PATH}/data-analyst`, {
      question,
      data,
      data_description: options.dataDescription || null,
      generate_charts: options.generateCharts !== false,
      idempotency_key: options.idempotencyKey || null,
      priority: options.priority || 0,
      webhook_url: options.webhookUrl || null,
      sync: options.sync !== false,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================
// Email Draft Agent
// ============================================

/**
 * Run the email draft agent to compose an email.
 *
 * @param {string} context - Background context for the email
 * @param {string} purpose - Purpose of the email
 * @param {Object} options - Configuration options
 * @param {string} options.tone - Tone: professional, friendly, formal, casual, empathetic, assertive
 * @param {string} options.recipientInfo - Information about the recipient
 * @param {string[]} options.previousEmails - Previous emails in thread
 * @param {boolean} options.includeSubject - Include subject line (default true)
 * @param {string} options.idempotencyKey - Unique key for deduplication
 * @param {number} options.priority - Task priority (0-10)
 * @param {string} options.webhookUrl - Webhook URL for completion
 * @param {boolean} options.sync - Wait for completion (default true)
 * @returns {Promise<Object>} Task response
 */
export async function runEmailDraftAgent(context, purpose, options = {}) {
  try {
    const response = await api.post(`${BASE_PATH}/email-draft`, {
      context,
      purpose,
      tone: options.tone || 'professional',
      recipient_info: options.recipientInfo || null,
      previous_emails: options.previousEmails || null,
      include_subject: options.includeSubject !== false,
      idempotency_key: options.idempotencyKey || null,
      priority: options.priority || 0,
      webhook_url: options.webhookUrl || null,
      sync: options.sync !== false,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================
// Content Repurposing Agent
// ============================================

/**
 * Run the content repurposing agent to transform content into multiple formats.
 *
 * @param {string} content - Source content to repurpose
 * @param {string} sourceFormat - Format of the source (article, report, etc.)
 * @param {string[]} targetFormats - Target formats (tweet_thread, linkedin_post, etc.)
 * @param {Object} options - Configuration options
 * @param {boolean} options.preserveKeyPoints - Preserve key points (default true)
 * @param {boolean} options.adaptLength - Adapt length for format (default true)
 * @param {string} options.idempotencyKey - Unique key for deduplication
 * @param {number} options.priority - Task priority (0-10)
 * @param {string} options.webhookUrl - Webhook URL for completion
 * @param {boolean} options.sync - Wait for completion (default true)
 * @returns {Promise<Object>} Task response
 */
export async function runContentRepurposeAgent(content, sourceFormat, targetFormats, options = {}) {
  try {
    const response = await api.post(`${BASE_PATH}/content-repurpose`, {
      content,
      source_format: sourceFormat,
      target_formats: targetFormats,
      preserve_key_points: options.preserveKeyPoints !== false,
      adapt_length: options.adaptLength !== false,
      idempotency_key: options.idempotencyKey || null,
      priority: options.priority || 0,
      webhook_url: options.webhookUrl || null,
      sync: options.sync !== false,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================
// Proofreading Agent
// ============================================

/**
 * Run the proofreading agent for grammar, style, and clarity checking.
 *
 * @param {string} text - Text to proofread
 * @param {Object} options - Configuration options
 * @param {string} options.styleGuide - Style guide: ap, chicago, apa, mla
 * @param {string[]} options.focusAreas - Focus areas (grammar, spelling, clarity, etc.)
 * @param {boolean} options.preserveVoice - Preserve author's voice (default true)
 * @param {string} options.idempotencyKey - Unique key for deduplication
 * @param {number} options.priority - Task priority (0-10)
 * @param {string} options.webhookUrl - Webhook URL for completion
 * @param {boolean} options.sync - Wait for completion (default true)
 * @returns {Promise<Object>} Task response
 */
export async function runProofreadingAgent(text, options = {}) {
  try {
    const response = await api.post(`${BASE_PATH}/proofreading`, {
      text,
      style_guide: options.styleGuide || null,
      focus_areas: options.focusAreas || null,
      preserve_voice: options.preserveVoice !== false,
      idempotency_key: options.idempotencyKey || null,
      priority: options.priority || 0,
      webhook_url: options.webhookUrl || null,
      sync: options.sync !== false,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================
// Report Analyst Agent
// ============================================

/**
 * Run the report analyst agent to analyze, summarize, compare, or ask questions about reports.
 *
 * @param {string} runId - Report run ID to analyze
 * @param {Object} options - Configuration options
 * @param {string} options.analysisType - Analysis type: 'summarize', 'insights', 'compare', 'qa'
 * @param {string} options.question - Question text (required for 'qa' type)
 * @param {string} options.compareRunId - Second run ID (required for 'compare' type)
 * @param {string[]} options.focusAreas - Optional areas to focus on
 * @param {string} options.idempotencyKey - Unique key for deduplication
 * @param {number} options.priority - Task priority (0-10)
 * @param {string} options.webhookUrl - Webhook URL for completion
 * @param {boolean} options.sync - Wait for completion (default true)
 * @returns {Promise<Object>} Task response
 */
export async function runReportAnalystAgent(runId, options = {}) {
  try {
    const response = await api.post(`${BASE_PATH}/report-analyst`, {
      run_id: runId,
      analysis_type: options.analysisType || 'summarize',
      question: options.question || null,
      compare_run_id: options.compareRunId || null,
      focus_areas: options.focusAreas || null,
      idempotency_key: options.idempotencyKey || null,
      priority: options.priority || 0,
      webhook_url: options.webhookUrl || null,
      sync: options.sync !== false,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Generate a report from an agent task result.
 *
 * @param {string} taskId - Agent task ID whose result provides context
 * @param {Object} config - Report generation config
 * @param {string} config.templateId - Template to use
 * @param {string} config.connectionId - Database connection to use
 * @param {string} config.startDate - Report start date (YYYY-MM-DD)
 * @param {string} config.endDate - Report end date (YYYY-MM-DD)
 * @param {Object} config.keyValues - Additional key-value parameters
 * @param {boolean} config.docx - Generate DOCX
 * @param {boolean} config.xlsx - Generate XLSX
 * @returns {Promise<Object>} Job info with job_id
 */
export async function generateReportFromTask(taskId, config = {}) {
  try {
    const response = await api.post(`${BASE_PATH}/tasks/${taskId}/generate-report`, {
      template_id: config.templateId,
      connection_id: config.connectionId,
      start_date: config.startDate,
      end_date: config.endDate,
      key_values: config.keyValues || null,
      docx: config.docx || false,
      xlsx: config.xlsx || false,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================
// Task Management
// ============================================

/**
 * Get a task by ID.
 *
 * @param {string} taskId - Task identifier
 * @returns {Promise<Object>} Task details including status, progress, and result
 */
export async function getTask(taskId) {
  try {
    const response = await api.get(`${BASE_PATH}/tasks/${taskId}`);
    const payload = response.data;
    if (payload && typeof payload === 'object' && payload.task) {
      return payload.task;
    }
    return payload;
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * List tasks with optional filtering.
 *
 * @param {Object} options - Filter options
 * @param {string} options.agentType - Filter by agent type
 * @param {string} options.status - Filter by status
 * @param {string} options.userId - Filter by user ID
 * @param {number} options.limit - Maximum results (default 50, max 100)
 * @param {number} options.offset - Number to skip (default 0)
 * @returns {Promise<Object>} List of tasks with pagination info
 */
export async function listTasks(options = {}) {
  try {
    const params = {};
    if (options.agentType) params.agent_type = options.agentType;
    if (options.status) params.status = options.status;
    if (options.userId) params.user_id = options.userId;
    if (options.limit) params.limit = options.limit;
    if (options.offset) params.offset = options.offset;

    const response = await api.get(`${BASE_PATH}/tasks`, { params });
    const payload = response.data;
    if (Array.isArray(payload)) {
      return { tasks: payload, total: payload.length };
    }
    if (payload && typeof payload === 'object') {
      const tasks = asArray(payload, ['tasks', 'items', 'results']);
      return { ...payload, tasks, total: payload.total ?? payload.count ?? tasks.length };
    }
    return { tasks: [], total: 0 };
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Cancel a pending or running task.
 *
 * @param {string} taskId - Task identifier
 * @param {string} reason - Optional cancellation reason
 * @returns {Promise<Object>} Updated task with cancelled status
 */
export async function cancelTask(taskId, reason = null) {
  try {
    const response = await api.post(`${BASE_PATH}/tasks/${taskId}/cancel`, {
      reason,
    });
    const payload = response.data;
    if (payload && typeof payload === 'object' && payload.task) {
      return payload.task;
    }
    return payload;
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Retry a failed task.
 *
 * @param {string} taskId - Task identifier
 * @returns {Promise<Object>} Updated task after retry
 */
export async function retryTask(taskId) {
  try {
    const response = await api.post(`${BASE_PATH}/tasks/${taskId}/retry`);
    const payload = response.data;
    if (payload && typeof payload === 'object' && payload.task) {
      return payload.task;
    }
    return payload;
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Get audit events for a task.
 *
 * @param {string} taskId - Task identifier
 * @param {number} limit - Maximum events (default 100, max 500)
 * @returns {Promise<Object[]>} List of task events
 */
export async function getTaskEvents(taskId, limit = 100) {
  try {
    const response = await api.get(`${BASE_PATH}/tasks/${taskId}/events`, {
      params: { limit },
    });
    return asArray(response.data, ['events', 'items', 'results']);
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================
// Polling Helper
// ============================================

/**
 * Poll a task until it reaches a terminal state.
 *
 * @param {string} taskId - Task identifier
 * @param {Object} options - Polling options
 * @param {number} options.intervalMs - Polling interval in ms (default 1000)
 * @param {number} options.timeoutMs - Maximum wait time in ms (default 300000 = 5 min)
 * @param {Function} options.onProgress - Callback for progress updates (receives task)
 * @param {AbortSignal} options.signal - AbortSignal for cancellation
 * @returns {Promise<Object>} Final task state
 */
export async function pollTaskUntilComplete(taskId, options = {}) {
  const {
    intervalMs = 1000,
    timeoutMs = 300000,
    onProgress = null,
    signal = null,
  } = options;

  const startTime = Date.now();
  const terminalStatuses = ['completed', 'failed', 'cancelled'];

  while (true) {
    // Check for abort
    if (signal?.aborted) {
      throw new AgentError('POLLING_ABORTED', 'Polling was aborted', false);
    }

    // Check for timeout
    if (Date.now() - startTime > timeoutMs) {
      throw new AgentError('POLLING_TIMEOUT', `Task did not complete within ${timeoutMs}ms`, true);
    }

    // Fetch task status
    const task = await getTask(taskId);

    // Report progress
    if (onProgress) {
      try {
        onProgress(task);
      } catch (e) {
        console.warn('Progress callback error:', e);
      }
    }

    // Check if terminal
    if (terminalStatuses.includes(task.status)) {
      return task;
    }

    // Wait before next poll
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
}

/**
 * Run research agent and poll until complete (convenience method).
 *
 * @param {string} topic - Topic to research
 * @param {Object} options - Same as runResearchAgent + polling options
 * @returns {Promise<Object>} Final task state with result
 */
export async function runResearchAndWait(topic, options = {}) {
  // Always run async for polling
  const task = await runResearchAgent(topic, { ...options, sync: false });

  return pollTaskUntilComplete(task.task_id, {
    intervalMs: options.pollIntervalMs,
    timeoutMs: options.pollTimeoutMs,
    onProgress: options.onProgress,
    signal: options.signal,
  });
}

// ============================================
// Utility
// ============================================

/**
 * List available agent types.
 *
 * @returns {Promise<Object>} List of agent types with descriptions
 */
export async function listAgentTypes() {
  try {
    const response = await api.get(`${BASE_PATH}/types`);
    const payload = response.data;
    if (Array.isArray(payload)) {
      return { types: payload };
    }
    if (payload && typeof payload === 'object') {
      return { ...payload, types: asArray(payload, ['types', 'items', 'results']) };
    }
    return { types: [] };
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Get service statistics.
 *
 * @returns {Promise<Object>} Task counts by status
 */
export async function getStats() {
  try {
    const response = await api.get(`${BASE_PATH}/stats`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Health check for agents service.
 *
 * @returns {Promise<Object>} Health status
 */
export async function healthCheck() {
  try {
    const response = await api.get(`${BASE_PATH}/health`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================
// SSE Progress Streaming (Trade-off 2)
// ============================================

/**
 * Stream real-time progress updates for a task via Server-Sent Events.
 *
 * Returns an EventSource-like controller with cleanup. Prefer this over
 * polling when you need instant progress feedback in the UI.
 *
 * @param {string} taskId - Task identifier
 * @param {Object} options - Streaming options
 * @param {Function} options.onProgress - Called on progress updates (receives {event, data})
 * @param {Function} options.onComplete - Called when task reaches terminal state
 * @param {Function} options.onError - Called on stream errors
 * @param {number} options.pollInterval - Poll interval in seconds (default 0.5)
 * @param {number} options.timeout - Stream timeout in seconds (default 300)
 * @returns {Object} Controller with { close() } method
 */
export function streamTaskProgress(taskId, options = {}) {
  const {
    onProgress = null,
    onComplete = null,
    onError = null,
    pollInterval = 0.5,
    timeout = 300,
  } = options;

  const params = new URLSearchParams({
    poll_interval: String(pollInterval),
    timeout: String(timeout),
  });

  const url = toApiUrl(`${BASE_PATH}/tasks/${taskId}/stream?${params}`);

  // Use EventSource for native SSE support
  const eventSource = new EventSource(url);
  let closed = false;

  eventSource.onmessage = (event) => {
    if (closed) return;

    try {
      const payload = JSON.parse(event.data);

      if (payload.event === 'progress' && onProgress) {
        onProgress(payload.data);
      } else if (payload.event === 'complete') {
        if (onComplete) onComplete(payload.data);
        eventSource.close();
        closed = true;
      } else if (payload.event === 'heartbeat') {
        // Connection keep-alive — no action needed
      } else if (payload.event === 'error') {
        // DB_ERROR is transient — server will retry automatically
        if (payload.data.code === 'DB_ERROR') return;
        if (onError) {
          onError(new AgentError(
            payload.data.code || 'STREAM_ERROR',
            payload.data.message || 'Stream error',
            false,
          ));
        }
        eventSource.close();
        closed = true;
      }
    } catch (e) {
      console.warn('Failed to parse SSE event:', e);
    }
  };

  eventSource.onerror = (event) => {
    if (closed) return;

    // EventSource auto-reconnects on transient errors.
    // Only propagate if the connection is truly dead.
    if (eventSource.readyState === EventSource.CLOSED) {
      if (onError) {
        onError(new AgentError('SSE_CONNECTION_CLOSED', 'SSE connection closed', true));
      }
      closed = true;
    }
  };

  return {
    close() {
      if (!closed) {
        closed = true;
        eventSource.close();
      }
    },
  };
}

/**
 * Run research agent with SSE progress streaming (convenience method).
 *
 * Creates the task asynchronously and immediately starts streaming progress.
 * Returns a promise that resolves with the final task state.
 *
 * @param {string} topic - Topic to research
 * @param {Object} options - Same as runResearchAgent + streaming options
 * @param {Function} options.onProgress - Progress callback
 * @returns {Promise<Object>} Final task state with result
 */
export async function runResearchWithStreaming(topic, options = {}) {
  // Create the task asynchronously first
  const task = await runResearchAgent(topic, { ...options, sync: false });

  // Then wrap only the SSE streaming in a promise
  return new Promise((resolve, reject) => {
    streamTaskProgress(task.task_id, {
      onProgress: options.onProgress,
      onComplete: (data) => resolve(data),
      onError: (err) => reject(err),
      pollInterval: options.pollInterval,
      timeout: options.timeout,
    });
  });
}

// ============================================
// Generate Idempotency Key Helper
// ============================================

/**
 * Generate a unique idempotency key for a research request.
 * Use this to ensure duplicate requests return the same task.
 *
 * @param {string} userId - User identifier
 * @param {string} topic - Research topic
 * @param {Object} options - Request options (depth, focusAreas, etc.)
 * @returns {string} Idempotency key
 */
export function generateIdempotencyKey(userId, topic, options = {}) {
  const parts = [
    userId,
    topic.toLowerCase().trim(),
    options.depth || 'comprehensive',
    (options.focusAreas || []).sort().join(','),
    options.maxSections || 5,
  ];
  return btoa(parts.join('|')).replace(/[^a-zA-Z0-9]/g, '').slice(0, 64);
}

export default {
  // Research
  runResearchAgent,
  runResearchAndWait,
  runResearchWithStreaming,

  // Data Analyst
  runDataAnalystAgent,

  // Email Draft
  runEmailDraftAgent,

  // Content Repurpose
  runContentRepurposeAgent,

  // Proofreading
  runProofreadingAgent,

  // Report Analyst
  runReportAnalystAgent,
  generateReportFromTask,

  // Task Management
  getTask,
  listTasks,
  cancelTask,
  retryTask,
  getTaskEvents,

  // Polling
  pollTaskUntilComplete,

  // SSE Streaming
  streamTaskProgress,

  // Utility
  listAgentTypes,
  getStats,
  healthCheck,
  generateIdempotencyKey,

  // Error Types
  AgentError,
  ValidationError,
  TaskNotFoundError,
  TaskConflictError,
};
