import { useMemo, useState, useCallback } from 'react'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import api, { API_BASE } from '@/api/client.js'

export const parseJsonInput = (value, toast, label) => {
  const trimmed = (value || '').trim()
  if (!trimmed) return undefined
  try {
    return JSON.parse(trimmed)
  } catch (error) {
    toast.show(`Invalid ${label} JSON`, 'error')
    return null
  }
}

export const splitList = (value) => (
  (value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
)

export function useOpsConsole() {
  const toast = useToast()
  const { execute } = useInteraction()
  const [busy, setBusy] = useState(false)
  const [lastResponse, setLastResponse] = useState(null)

  const [apiKey, setApiKey] = useState('')
  const [bearerToken, setBearerToken] = useState('')

  const authHeaders = useMemo(() => {
    const headers = {}
    const trimmedKey = apiKey.trim()
    const trimmedToken = bearerToken.trim()
    if (trimmedKey) headers['X-API-Key'] = trimmedKey
    if (trimmedToken) headers.Authorization = `Bearer ${trimmedToken}`
    return headers
  }, [apiKey, bearerToken])

  const runRequest = useCallback(async ({ method = 'get', url, data, headers = {}, onSuccess } = {}) => {
    const verb = method.toLowerCase()
    const interactionType = verb === 'delete'
      ? InteractionType.DELETE
      : verb === 'put' || verb === 'patch'
        ? InteractionType.UPDATE
        : verb === 'post'
          ? InteractionType.CREATE
          : InteractionType.EXECUTE
    const reversibility = verb === 'delete' ? Reversibility.IRREVERSIBLE : Reversibility.SYSTEM_MANAGED

    return execute({
      type: interactionType,
      label: `${verb.toUpperCase()} ${url}`,
      reversibility,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      blocksNavigation: false,
      intent: {
        method: verb,
        url,
      },
      action: async () => {
        setBusy(true)
        setLastResponse({
          pending: true,
          method: verb,
          url,
          timestamp: new Date().toISOString(),
        })
        try {
          const response = await api.request({
            method: verb,
            url,
            data,
            headers: {
              ...authHeaders,
              ...headers,
            },
          })
          const payload = response.data
          setLastResponse({
            method: verb,
            url,
            status: response.status,
            data: payload,
            timestamp: new Date().toISOString(),
          })
          if (onSuccess) onSuccess(payload)
          toast.show(`Success: ${verb.toUpperCase()} ${url}`, 'success')
          return payload
        } catch (error) {
          const status = error.response?.status
          const payload = error.response?.data || { message: error.userMessage || error.message }
          setLastResponse({
            method: verb,
            url,
            status,
            error: payload,
            timestamp: new Date().toISOString(),
          })
          toast.show(`Failed: ${verb.toUpperCase()} ${url}`, 'error')
          throw error
        } finally {
          setBusy(false)
        }
      },
    })
  }, [execute, authHeaders, toast])

  const responseBody = useMemo(() => {
    if (!lastResponse) return 'Run an action to view the response payload.'
    if (lastResponse.pending) return 'Waiting for response...'
    const payload = lastResponse.data || lastResponse.error || {}
    return JSON.stringify(payload, null, 2)
  }, [lastResponse])

  return {
    toast,
    busy,
    lastResponse,
    apiKey,
    setApiKey,
    bearerToken,
    setBearerToken,
    runRequest,
    responseBody,
    API_BASE,
  }
}

export function useAuthUsersState() {
  const [registerEmail, setRegisterEmail] = useState('')
  const [registerPassword, setRegisterPassword] = useState('')
  const [registerName, setRegisterName] = useState('')
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [userId, setUserId] = useState('')

  return {
    registerEmail, setRegisterEmail,
    registerPassword, setRegisterPassword,
    registerName, setRegisterName,
    loginEmail, setLoginEmail,
    loginPassword, setLoginPassword,
    userId, setUserId,
  }
}

export function useJobsSchedulesState() {
  const [jobTemplateId, setJobTemplateId] = useState('')
  const [jobConnectionId, setJobConnectionId] = useState('')
  const [jobStartDate, setJobStartDate] = useState('')
  const [jobEndDate, setJobEndDate] = useState('')
  const [jobDocx, setJobDocx] = useState(false)
  const [jobXlsx, setJobXlsx] = useState(false)
  const [jobKeyValues, setJobKeyValues] = useState('')
  const [jobBatchIds, setJobBatchIds] = useState('')
  const [jobLimit, setJobLimit] = useState(20)
  const [scheduleId, setScheduleId] = useState('')

  return {
    jobTemplateId, setJobTemplateId,
    jobConnectionId, setJobConnectionId,
    jobStartDate, setJobStartDate,
    jobEndDate, setJobEndDate,
    jobDocx, setJobDocx,
    jobXlsx, setJobXlsx,
    jobKeyValues, setJobKeyValues,
    jobBatchIds, setJobBatchIds,
    jobLimit, setJobLimit,
    scheduleId, setScheduleId,
  }
}

export function useAnalyzeExtrasState() {
  const [compareId1, setCompareId1] = useState('')
  const [compareId2, setCompareId2] = useState('')
  const [commentAnalysisId, setCommentAnalysisId] = useState('')
  const [commentUserId, setCommentUserId] = useState('')
  const [commentUserName, setCommentUserName] = useState('')
  const [commentContent, setCommentContent] = useState('')
  const [commentElementType, setCommentElementType] = useState('')
  const [commentElementId, setCommentElementId] = useState('')

  return {
    compareId1, setCompareId1,
    compareId2, setCompareId2,
    commentAnalysisId, setCommentAnalysisId,
    commentUserId, setCommentUserId,
    commentUserName, setCommentUserName,
    commentContent, setCommentContent,
    commentElementType, setCommentElementType,
    commentElementId, setCommentElementId,
  }
}

export function useShareLinksState() {
  const [shareAnalysisId, setShareAnalysisId] = useState('')
  const [shareAccessLevel, setShareAccessLevel] = useState('view')
  const [shareExpiresHours, setShareExpiresHours] = useState('')
  const [shareAllowedEmails, setShareAllowedEmails] = useState('')
  const [sharePasswordProtected, setSharePasswordProtected] = useState(false)

  return {
    shareAnalysisId, setShareAnalysisId,
    shareAccessLevel, setShareAccessLevel,
    shareExpiresHours, setShareExpiresHours,
    shareAllowedEmails, setShareAllowedEmails,
    sharePasswordProtected, setSharePasswordProtected,
  }
}

export function useEnrichmentState() {
  const [enrichmentSourceId, setEnrichmentSourceId] = useState('')
  return { enrichmentSourceId, setEnrichmentSourceId }
}

export function useChartsState() {
  const [chartData, setChartData] = useState('[{"month":"Jan","value":120},{"month":"Feb","value":140}]')
  const [chartType, setChartType] = useState('bar')
  const [chartXField, setChartXField] = useState('month')
  const [chartYFields, setChartYFields] = useState('value')
  const [chartTitle, setChartTitle] = useState('')
  const [chartMaxSuggestions, setChartMaxSuggestions] = useState(3)

  return {
    chartData, setChartData,
    chartType, setChartType,
    chartXField, setChartXField,
    chartYFields, setChartYFields,
    chartTitle, setChartTitle,
    chartMaxSuggestions, setChartMaxSuggestions,
  }
}
