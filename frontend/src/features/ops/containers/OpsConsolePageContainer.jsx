import { useMemo, useState } from 'react'
import {
  Box,
  Stack,
  Typography,
  TextField,
  Button,
  Divider,
  Grid,
  FormControlLabel,
  Switch,
  Chip,
  MenuItem,
} from '@mui/material'
import PageHeader from '@/components/layout/PageHeader.jsx'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import TemplateSelector from '@/components/common/TemplateSelector'
import api, { API_BASE } from '@/api/client.js'

const parseJsonInput = (value, toast, label) => {
  const trimmed = (value || '').trim()
  if (!trimmed) return undefined
  try {
    return JSON.parse(trimmed)
  } catch (error) {
    toast.show(`Invalid ${label} JSON`, 'error')
    return null
  }
}

const splitList = (value) => (
  (value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
)

export default function OpsConsolePage() {
  const toast = useToast()
  const { execute } = useInteraction()
  const [busy, setBusy] = useState(false)
  const [lastResponse, setLastResponse] = useState(null)

  const [apiKey, setApiKey] = useState('')
  const [bearerToken, setBearerToken] = useState('')

  const [registerEmail, setRegisterEmail] = useState('')
  const [registerPassword, setRegisterPassword] = useState('')
  const [registerName, setRegisterName] = useState('')

  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')

  const [userId, setUserId] = useState('')

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

  const [compareId1, setCompareId1] = useState('')
  const [compareId2, setCompareId2] = useState('')

  const [commentAnalysisId, setCommentAnalysisId] = useState('')
  const [commentUserId, setCommentUserId] = useState('')
  const [commentUserName, setCommentUserName] = useState('')
  const [commentContent, setCommentContent] = useState('')
  const [commentElementType, setCommentElementType] = useState('')
  const [commentElementId, setCommentElementId] = useState('')

  const [shareAnalysisId, setShareAnalysisId] = useState('')
  const [shareAccessLevel, setShareAccessLevel] = useState('view')
  const [shareExpiresHours, setShareExpiresHours] = useState('')
  const [shareAllowedEmails, setShareAllowedEmails] = useState('')
  const [sharePasswordProtected, setSharePasswordProtected] = useState(false)

  const [enrichmentSourceId, setEnrichmentSourceId] = useState('')

  const [chartData, setChartData] = useState('[{"month":"Jan","value":120},{"month":"Feb","value":140}]')
  const [chartType, setChartType] = useState('bar')
  const [chartXField, setChartXField] = useState('month')
  const [chartYFields, setChartYFields] = useState('value')
  const [chartTitle, setChartTitle] = useState('')
  const [chartMaxSuggestions, setChartMaxSuggestions] = useState(3)

  const authHeaders = useMemo(() => {
    const headers = {}
    const trimmedKey = apiKey.trim()
    const trimmedToken = bearerToken.trim()
    if (trimmedKey) headers['X-API-Key'] = trimmedKey
    if (trimmedToken) headers.Authorization = `Bearer ${trimmedToken}`
    return headers
  }, [apiKey, bearerToken])

  const runRequest = async ({ method = 'get', url, data, headers = {}, onSuccess } = {}) => {
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
  }

  const responseBody = useMemo(() => {
    if (!lastResponse) return 'Run an action to view the response payload.'
    if (lastResponse.pending) return 'Waiting for response...'
    const payload = lastResponse.data || lastResponse.error || {}
    return JSON.stringify(payload, null, 2)
  }, [lastResponse])

  return (
    <Box sx={{ py: 3, px: { xs: 2, md: 3 } }}>
      <Stack spacing={3}>
        <PageHeader
          eyebrow="Operations"
          title="Ops Console"
          description="Direct access to health checks, auth, jobs, schedules, and AI utilities that are not surfaced elsewhere."
        />

        <Surface>
          <SectionHeader
            title="Request Context"
            subtitle="Provide API key or bearer token to authorize protected endpoints."
          />
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Stack spacing={1}>
                <Typography variant="caption" color="text.secondary">
                  API Base
                </Typography>
                <Chip label={API_BASE} variant="outlined" />
              </Stack>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="X-API-Key"
                value={apiKey}
                onChange={(event) => setApiKey(event.target.value)}
                size="small"
                placeholder="Optional"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Bearer Token"
                value={bearerToken}
                onChange={(event) => setBearerToken(event.target.value)}
                size="small"
                placeholder="Paste access token"
              />
            </Grid>
          </Grid>
        </Surface>

        <Surface>
          <SectionHeader
            title="Auth & Users"
            subtitle="Register users, obtain tokens, and manage user records."
          />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Register</Typography>
                <TextField
                  fullWidth
                  label="Email"
                  value={registerEmail}
                  onChange={(event) => setRegisterEmail(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Password"
                  value={registerPassword}
                  onChange={(event) => setRegisterPassword(event.target.value)}
                  size="small"
                  type="password"
                />
                <TextField
                  fullWidth
                  label="Full Name (optional)"
                  value={registerName}
                  onChange={(event) => setRegisterName(event.target.value)}
                  size="small"
                />
                <Button
                  variant="contained"
                  disabled={busy}
                  onClick={() => {
                    if (!registerEmail || !registerPassword) {
                      toast.show('Email and password are required', 'warning')
                      return
                    }
                    const payload = {
                      email: registerEmail,
                      password: registerPassword,
                    }
                    if (registerName) payload.full_name = registerName
                    runRequest({ method: 'post', url: '/auth/register', data: payload })
                  }}
                >
                  Register User
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Login</Typography>
                <TextField
                  fullWidth
                  label="Email / Username"
                  value={loginEmail}
                  onChange={(event) => setLoginEmail(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Password"
                  value={loginPassword}
                  onChange={(event) => setLoginPassword(event.target.value)}
                  size="small"
                  type="password"
                />
                <Button
                  variant="contained"
                  disabled={busy}
                  onClick={() => {
                    if (!loginEmail || !loginPassword) {
                      toast.show('Login requires email and password', 'warning')
                      return
                    }
                    const params = new URLSearchParams()
                    params.append('username', loginEmail)
                    params.append('password', loginPassword)
                    runRequest({
                      method: 'post',
                      url: '/auth/jwt/login',
                      data: params,
                      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                      onSuccess: (payload) => {
                        if (payload?.access_token) {
                          setBearerToken(payload.access_token)
                          toast.show('Token saved to bearer field', 'info')
                        }
                      },
                    })
                  }}
                >
                  Get Access Token
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12}>
              <Divider />
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">User Management</Typography>
                <TextField
                  fullWidth
                  label="User ID"
                  value={userId}
                  onChange={(event) => setUserId(event.target.value)}
                  size="small"
                  placeholder="UUID"
                />
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  <Button
                    variant="outlined"
                    disabled={busy}
                    onClick={() => runRequest({ url: '/users' })}
                  >
                    List Users
                  </Button>
                  <Button
                    variant="outlined"
                    disabled={busy}
                    onClick={() => {
                      if (!userId) {
                        toast.show('User ID required', 'warning')
                        return
                      }
                      runRequest({ url: `/users/${encodeURIComponent(userId)}` })
                    }}
                  >
                    Get User
                  </Button>
                  <Button
                    variant="outlined"
                    disabled={busy}
                    onClick={() => {
                      if (!userId) {
                        toast.show('User ID required', 'warning')
                        return
                      }
                      runRequest({ method: 'delete', url: `/users/${encodeURIComponent(userId)}` })
                    }}
                    sx={{ color: 'text.secondary' }}
                  >
                    Delete User
                  </Button>
                </Stack>
              </Stack>
            </Grid>
          </Grid>
        </Surface>

        <Surface>
          <SectionHeader
            title="Health & Ops"
            subtitle="Run service health checks and diagnostics."
          />
          <Stack spacing={1.5}>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health' })}>/health</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/healthz' })}>/healthz</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/ready' })}>/ready</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/readyz' })}>/readyz</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/detailed' })}>/health/detailed</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/token-usage' })}>/health/token-usage</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/email' })}>/health/email</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/email/test' })}>/health/email/test</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ method: 'post', url: '/health/email/refresh' })}>/health/email/refresh</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/scheduler' })}>/health/scheduler</Button>
            </Stack>
          </Stack>
        </Surface>
        <Surface>
          <SectionHeader
            title="Jobs & Schedules"
            subtitle="Trigger job runs, inspect active jobs, and manage schedules."
          />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Run Report Job</Typography>
                <TemplateSelector
                  value={jobTemplateId}
                  onChange={setJobTemplateId}
                  label="Template"
                  size="small"
                  fullWidth
                  showAll
                />
                <ConnectionSelector
                  value={jobConnectionId}
                  onChange={setJobConnectionId}
                  label="Connection (optional)"
                  size="small"
                  fullWidth
                  showStatus
                />
                <Grid container spacing={1}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Start Date"
                      value={jobStartDate}
                      onChange={(event) => setJobStartDate(event.target.value)}
                      size="small"
                      placeholder="YYYY-MM-DD"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="End Date"
                      value={jobEndDate}
                      onChange={(event) => setJobEndDate(event.target.value)}
                      size="small"
                      placeholder="YYYY-MM-DD"
                    />
                  </Grid>
                </Grid>
                <Stack direction="row" spacing={2}>
                  <FormControlLabel
                    control={<Switch checked={jobDocx} onChange={(event) => setJobDocx(event.target.checked)} />}
                    label="DOCX"
                  />
                  <FormControlLabel
                    control={<Switch checked={jobXlsx} onChange={(event) => setJobXlsx(event.target.checked)} />}
                    label="XLSX"
                  />
                </Stack>
                <TextField
                  fullWidth
                  label="Key Values (JSON)"
                  value={jobKeyValues}
                  onChange={(event) => setJobKeyValues(event.target.value)}
                  size="small"
                  multiline
                  minRows={3}
                  placeholder='{"PARAM:region":"US"}'
                />
                <TextField
                  fullWidth
                  label="Batch IDs (comma separated)"
                  value={jobBatchIds}
                  onChange={(event) => setJobBatchIds(event.target.value)}
                  size="small"
                />
                <Button
                  variant="contained"
                  disabled={busy}
                  onClick={() => {
                    if (!jobTemplateId || !jobStartDate || !jobEndDate) {
                      toast.show('Template ID, start date, and end date are required', 'warning')
                      return
                    }
                    const keyValues = parseJsonInput(jobKeyValues, toast, 'key values')
                    if (keyValues === null) return
                    const payload = {
                      template_id: jobTemplateId,
                      connection_id: jobConnectionId || undefined,
                      start_date: jobStartDate,
                      end_date: jobEndDate,
                      docx: jobDocx,
                      xlsx: jobXlsx,
                      key_values: keyValues,
                      batch_ids: splitList(jobBatchIds),
                    }
                    runRequest({ method: 'post', url: '/jobs/run-report', data: payload })
                  }}
                >
                  Queue Job
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Active Jobs</Typography>
                <TextField
                  fullWidth
                  label="Limit"
                  type="number"
                  value={jobLimit}
                  onChange={(event) => setJobLimit(Number(event.target.value) || 0)}
                  size="small"
                  inputProps={{ min: 1, max: 200 }}
                />
                <Button
                  variant="outlined"
                  disabled={busy}
                  onClick={() => {
                    const limit = jobLimit > 0 ? jobLimit : 20
                    runRequest({ url: `/jobs/active?limit=${limit}` })
                  }}
                >
                  List Active Jobs
                </Button>
                <Divider />
                <Typography variant="subtitle2">Schedule Controls</Typography>
                <TextField
                  fullWidth
                  label="Schedule ID"
                  value={scheduleId}
                  onChange={(event) => setScheduleId(event.target.value)}
                  size="small"
                />
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  <Button
                    variant="outlined"
                    disabled={busy}
                    onClick={() => {
                      if (!scheduleId) {
                        toast.show('Schedule ID required', 'warning')
                        return
                      }
                      runRequest({ method: 'post', url: `/reports/schedules/${encodeURIComponent(scheduleId)}/trigger` })
                    }}
                  >
                    Trigger
                  </Button>
                  <Button
                    variant="outlined"
                    disabled={busy}
                    onClick={() => {
                      if (!scheduleId) {
                        toast.show('Schedule ID required', 'warning')
                        return
                      }
                      runRequest({ method: 'post', url: `/reports/schedules/${encodeURIComponent(scheduleId)}/pause` })
                    }}
                  >
                    Pause
                  </Button>
                  <Button
                    variant="outlined"
                    disabled={busy}
                    onClick={() => {
                      if (!scheduleId) {
                        toast.show('Schedule ID required', 'warning')
                        return
                      }
                      runRequest({ method: 'post', url: `/reports/schedules/${encodeURIComponent(scheduleId)}/resume` })
                    }}
                  >
                    Resume
                  </Button>
                </Stack>
              </Stack>
            </Grid>
          </Grid>
        </Surface>
        <Surface>
          <SectionHeader
            title="Analyze v2 Extras"
            subtitle="Compare analyses, manage comments, create share links, and load config values."
          />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Compare Analyses</Typography>
                <TextField
                  fullWidth
                  label="Analysis ID 1"
                  value={compareId1}
                  onChange={(event) => setCompareId1(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Analysis ID 2"
                  value={compareId2}
                  onChange={(event) => setCompareId2(event.target.value)}
                  size="small"
                />
                <Button
                  variant="outlined"
                  disabled={busy}
                  onClick={() => {
                    if (!compareId1 || !compareId2) {
                      toast.show('Both analysis IDs are required', 'warning')
                      return
                    }
                    runRequest({
                      method: 'post',
                      url: '/analyze/v2/compare',
                      data: {
                        analysis_id_1: compareId1,
                        analysis_id_2: compareId2,
                      },
                    })
                  }}
                >
                  Compare
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Comments</Typography>
                <TextField
                  fullWidth
                  label="Analysis ID"
                  value={commentAnalysisId}
                  onChange={(event) => setCommentAnalysisId(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="User ID"
                  value={commentUserId}
                  onChange={(event) => setCommentUserId(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="User Name"
                  value={commentUserName}
                  onChange={(event) => setCommentUserName(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Element Type (optional)"
                  value={commentElementType}
                  onChange={(event) => setCommentElementType(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Element ID (optional)"
                  value={commentElementId}
                  onChange={(event) => setCommentElementId(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Comment"
                  value={commentContent}
                  onChange={(event) => setCommentContent(event.target.value)}
                  size="small"
                  multiline
                  minRows={2}
                />
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  <Button
                    variant="outlined"
                    disabled={busy}
                    onClick={() => {
                      if (!commentAnalysisId) {
                        toast.show('Analysis ID is required', 'warning')
                        return
                      }
                      runRequest({ url: `/analyze/v2/${encodeURIComponent(commentAnalysisId)}/comments` })
                    }}
                  >
                    List Comments
                  </Button>
                  <Button
                    variant="contained"
                    disabled={busy}
                    onClick={() => {
                      if (!commentAnalysisId || !commentContent) {
                        toast.show('Analysis ID and comment content are required', 'warning')
                        return
                      }
                      runRequest({
                        method: 'post',
                        url: `/analyze/v2/${encodeURIComponent(commentAnalysisId)}/comments`,
                        data: {
                          content: commentContent,
                          user_id: commentUserId || undefined,
                          user_name: commentUserName || undefined,
                          element_type: commentElementType || undefined,
                          element_id: commentElementId || undefined,
                        },
                      })
                    }}
                  >
                    Add Comment
                  </Button>
                </Stack>
              </Stack>
            </Grid>
            <Grid item xs={12}>
              <Divider />
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Share Links</Typography>
                <TextField
                  fullWidth
                  label="Analysis ID"
                  value={shareAnalysisId}
                  onChange={(event) => setShareAnalysisId(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  select
                  label="Access Level"
                  value={shareAccessLevel}
                  onChange={(event) => setShareAccessLevel(event.target.value)}
                  size="small"
                >
                  <MenuItem value="view">View</MenuItem>
                  <MenuItem value="comment">Comment</MenuItem>
                  <MenuItem value="edit">Edit</MenuItem>
                </TextField>
                <TextField
                  fullWidth
                  label="Expires in Hours (optional)"
                  value={shareExpiresHours}
                  onChange={(event) => setShareExpiresHours(event.target.value)}
                  size="small"
                  type="number"
                />
                <TextField
                  fullWidth
                  label="Allowed Emails (comma separated)"
                  value={shareAllowedEmails}
                  onChange={(event) => setShareAllowedEmails(event.target.value)}
                  size="small"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={sharePasswordProtected}
                      onChange={(event) => setSharePasswordProtected(event.target.checked)}
                    />
                  }
                  label="Password Protected"
                />
                <Button
                  variant="contained"
                  disabled={busy}
                  onClick={() => {
                    if (!shareAnalysisId) {
                      toast.show('Analysis ID is required', 'warning')
                      return
                    }
                    const expires = shareExpiresHours ? Number(shareExpiresHours) : undefined
                    runRequest({
                      method: 'post',
                      url: `/analyze/v2/${encodeURIComponent(shareAnalysisId)}/share`,
                      data: {
                        access_level: shareAccessLevel,
                        expires_hours: Number.isFinite(expires) ? expires : undefined,
                        password_protected: sharePasswordProtected,
                        allowed_emails: splitList(shareAllowedEmails),
                      },
                    })
                  }}
                >
                  Create Share Link
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Config Endpoints</Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/analyze/v2/config/industries' })}>Industries</Button>
                  <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/analyze/v2/config/export-formats' })}>Export Formats</Button>
                  <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/analyze/v2/config/chart-types' })}>Chart Types</Button>
                  <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/analyze/v2/config/summary-modes' })}>Summary Modes</Button>
                </Stack>
              </Stack>
            </Grid>
          </Grid>
        </Surface>
        <Surface>
          <SectionHeader
            title="Enrichment Extras"
            subtitle="Legacy source-type endpoints and source lookups."
          />
          <Stack spacing={1.5}>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/enrichment/source-types' })}>/enrichment/source-types</Button>
              <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/enrichment/sources' })}>/enrichment/sources</Button>
            </Stack>
            <TextField
              fullWidth
              label="Source ID"
              value={enrichmentSourceId}
              onChange={(event) => setEnrichmentSourceId(event.target.value)}
              size="small"
            />
            <Button
              variant="outlined"
              disabled={busy}
              onClick={() => {
                if (!enrichmentSourceId) {
                  toast.show('Source ID required', 'warning')
                  return
                }
                runRequest({ url: `/enrichment/sources/${encodeURIComponent(enrichmentSourceId)}` })
              }}
            >
              Get Source
            </Button>
          </Stack>
        </Surface>

        <Surface>
          <SectionHeader
            title="Charts API"
            subtitle="Request chart analysis and generation directly."
          />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Analyze Data</Typography>
                <TextField
                  fullWidth
                  label="Data (JSON array)"
                  value={chartData}
                  onChange={(event) => setChartData(event.target.value)}
                  size="small"
                  multiline
                  minRows={4}
                />
                <TextField
                  fullWidth
                  label="Max Suggestions"
                  type="number"
                  value={chartMaxSuggestions}
                  onChange={(event) => setChartMaxSuggestions(Number(event.target.value) || 0)}
                  size="small"
                  inputProps={{ min: 1, max: 10 }}
                />
                <Button
                  variant="outlined"
                  disabled={busy}
                  onClick={() => {
                    const data = parseJsonInput(chartData, toast, 'chart data')
                    if (data === null) return
                    runRequest({
                      method: 'post',
                      url: '/charts/analyze?background=true',
                      data: {
                        data,
                        max_suggestions: chartMaxSuggestions || 3,
                      },
                    })
                  }}
                >
                  Analyze Charts
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2">Generate Chart</Typography>
                <TextField
                  fullWidth
                  label="Chart Type"
                  value={chartType}
                  onChange={(event) => setChartType(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="X Field"
                  value={chartXField}
                  onChange={(event) => setChartXField(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Y Fields (comma separated)"
                  value={chartYFields}
                  onChange={(event) => setChartYFields(event.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Title (optional)"
                  value={chartTitle}
                  onChange={(event) => setChartTitle(event.target.value)}
                  size="small"
                />
                <Button
                  variant="contained"
                  disabled={busy}
                  onClick={() => {
                    const data = parseJsonInput(chartData, toast, 'chart data')
                    if (data === null) return
                    runRequest({
                      method: 'post',
                      url: '/charts/generate?background=true',
                      data: {
                        data,
                        chart_type: chartType || 'bar',
                        x_field: chartXField,
                        y_fields: splitList(chartYFields),
                        title: chartTitle || undefined,
                      },
                    })
                  }}
                >
                  Generate Chart
                </Button>
              </Stack>
            </Grid>
          </Grid>
        </Surface>

        <Surface>
          <SectionHeader
            title="Latest Response"
            subtitle="Most recent API payload and status metadata."
          />
          <Stack spacing={1.5}>
            {lastResponse ? (
              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Chip label={`${(lastResponse.method || 'GET').toUpperCase()} ${lastResponse.url || ''}`} />
                {lastResponse.status && (
                  <Chip
                    label={`Status ${lastResponse.status}`}
                    color={lastResponse.status >= 200 && lastResponse.status < 300 ? 'success' : 'error'}
                    variant="outlined"
                  />
                )}
                {lastResponse.timestamp && (
                  <Chip label={new Date(lastResponse.timestamp).toLocaleTimeString()} variant="outlined" />
                )}
              </Stack>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No requests yet.
              </Typography>
            )}
            <Box
              component="pre"
              sx={{
                mt: 1,
                p: 2,
                borderRadius: 1,  // Figma spec: 8px
                backgroundColor: 'background.default',
                border: '1px solid',
                borderColor: 'divider',
                fontSize: '12px',
                overflow: 'auto',
                maxHeight: 320,
              }}
            >
              {responseBody}
            </Box>
          </Stack>
        </Surface>
      </Stack>
    </Box>
  )
}
