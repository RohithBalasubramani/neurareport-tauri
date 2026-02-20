import Grid from '@mui/material/Grid2'
import {
  Alert,
  alpha,
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  Chip,
  CircularProgress,
  Collapse,
  Divider,
  LinearProgress,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material'
import { neutral, palette, secondary } from '@/app/theme'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import FileUploadOutlinedIcon from '@mui/icons-material/FileUploadOutlined'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import { savePersistedCache } from '@/hooks/useBootstrapState.js'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import LoadingState from '@/components/feedback/LoadingState.jsx'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'
import Surface from '@/components/layout/Surface.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { confirmDelete } from '@/utils/confirmDelete'
import { resolveTemplatePreviewUrl, resolveTemplateThumbnailUrl } from '@/utils/preview'
import { buildLastEditInfo } from '@/utils/templateMeta'
import getSourceMeta from '../utils/templateSourceMeta'
import { buildDownloadUrl, surfaceStackSx, getTemplateKind } from '../utils/generateFeatureUtils'
import {
  deleteTemplateRequest,
  exportTemplateZip,
  getTemplateCatalog,
  importTemplateZip,
  isMock,
  listApprovedTemplates,
  mock,
  recommendTemplates,
  queueRecommendTemplates,
  withBase,
} from '../services/generateApi'

export function TemplatePicker({ selected, onToggle, outputFormats, setOutputFormats, tagFilter, setTagFilter, onEditTemplate }) {
  const templates = useAppStore((state) => state.templates)
  const templateCatalog = useAppStore((state) => state.templateCatalog)
  const setTemplates = useAppStore((state) => state.setTemplates)
  const setTemplateCatalog = useAppStore((state) => state.setTemplateCatalog)
  const removeTemplate = useAppStore((state) => state.removeTemplate)
  const queryClient = useQueryClient()
  const toast = useToast()
  const [deleting, setDeleting] = useState(null)
  const [activeTab, setActiveTab] = useState('all')
  const [nameQuery, setNameQuery] = useState('')
  const [showStarterInAll, setShowStarterInAll] = useState(true)
  const [requirement, setRequirement] = useState('')
  const [kindHints, setKindHints] = useState([])
  const [domainHints, setDomainHints] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [recommending, setRecommending] = useState(false)
  const [queueingRecommendations, setQueueingRecommendations] = useState(false)
  const [importing, setImporting] = useState(false)
  const [exporting, setExporting] = useState(null)
  const importInputRef = useRef(null)

  const templatesQuery = useQuery({
    queryKey: ['templates', isMock],
    queryFn: () => (isMock ? mock.listTemplates() : listApprovedTemplates()),
  })

  const catalogQuery = useQuery({
    queryKey: ['template-catalog', isMock],
    queryFn: () => {
      if (isMock) {
        return typeof mock.getTemplateCatalog === 'function' ? mock.getTemplateCatalog() : []
      }
      return getTemplateCatalog()
    },
  })

  const { data, isLoading, isFetching, isError, error } = templatesQuery
  const catalogData = catalogQuery.data

  useEffect(() => {
    if (data) {
      setTemplates(data)
      const state = useAppStore.getState()
      savePersistedCache({
        connections: state.savedConnections,
        templates: data,
        lastUsed: state.lastUsed,
      })
    }
  }, [data, setTemplates])

  useEffect(() => {
    if (catalogData) {
      setTemplateCatalog(catalogData)
    }
  }, [catalogData, setTemplateCatalog])

  const approved = useMemo(() => templates.filter((t) => t.status === 'approved'), [templates])
  const catalogPool = useMemo(
    () => (templateCatalog && templateCatalog.length ? templateCatalog : templates),
    [templateCatalog, templates],
  )
  const companyCandidates = useMemo(
    () => approved.filter((tpl) => String(tpl.source || 'company').toLowerCase() !== 'starter'),
    [approved],
  )
  const starterCandidates = useMemo(
    () => catalogPool.filter((tpl) => String(tpl.source || '').toLowerCase() === 'starter'),
    [catalogPool],
  )
  const allTags = useMemo(
    () => Array.from(new Set(companyCandidates.flatMap((tpl) => tpl.tags || []))),
    [companyCandidates],
  )

  const normalizedQuery = nameQuery.trim().toLowerCase()
  const applyNameFilter = useCallback(
    (items) => {
      if (!normalizedQuery) return items
      return items.filter((tpl) => (tpl.name || tpl.id || '').toLowerCase().includes(normalizedQuery))
    },
    [normalizedQuery],
  )
  const applyTagFilter = useCallback(
    (items) => {
      if (!tagFilter?.length) return items
      return items.filter((tpl) => (tpl.tags || []).some((tag) => tagFilter.includes(tag)))
    },
    [tagFilter],
  )

  const kindOptions = useMemo(
    () =>
      Array.from(
        new Set(
          catalogPool
            .map((tpl) => (tpl.kind || '').toLowerCase())
            .filter(Boolean),
        ),
      ),
    [catalogPool],
  )
  const domainOptions = useMemo(
    () =>
      Array.from(
        new Set(
          catalogPool
            .map((tpl) => (tpl.domain || '').trim())
            .filter(Boolean),
        ),
      ),
    [catalogPool],
  )

  const companyMatches = useMemo(
    () => applyNameFilter(applyTagFilter(companyCandidates)),
    [applyNameFilter, applyTagFilter, companyCandidates],
  )
  const starterMatches = useMemo(
    () => applyNameFilter(applyTagFilter(starterCandidates)),
    [applyNameFilter, applyTagFilter, starterCandidates],
  )

  const recommendTemplatesClient = isMock ? mock.recommendTemplates : recommendTemplates


  const handleRecommend = async () => {
    const prompt = requirement.trim()
    if (!prompt) {
      toast.show('Describe what you need before requesting recommendations.', 'info')
      return
    }
    setRecommending(true)
    try {
      const result = await recommendTemplatesClient({
        requirement: prompt,
        limit: 6,
        kinds: kindHints,
        domains: domainHints,
      })
      const recs = Array.isArray(result?.recommendations)
        ? result.recommendations
        : Array.isArray(result)
          ? result
          : []
      setRecommendations(recs)
      setActiveTab('recommended')
    } catch (err) {
      toast.show(String(err), 'error')
    } finally {
      setRecommending(false)
    }
  }

  const handleQueueRecommend = async () => {
    const prompt = requirement.trim()
    if (!prompt) {
      toast.show('Describe what you need before queueing recommendations.', 'info')
      return
    }
    setQueueingRecommendations(true)
    try {
      const response = await queueRecommendTemplates({
        requirement: prompt,
        limit: 6,
        kinds: kindHints,
        domains: domainHints,
      })
      if (response?.job_id) {
        toast.show('Recommendation job queued. Track it in Jobs.', 'success')
      } else {
        toast.show('Failed to queue recommendations.', 'error')
      }
    } catch (err) {
      toast.show(String(err), 'error')
    } finally {
      setQueueingRecommendations(false)
    }
  }

  const handleRequirementKeyDown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      handleRecommend()
    }
  }

  const handleFindInAll = (templateName) => {
    const value = templateName || ""
    setNameQuery(value)
    setShowStarterInAll(true)
    setActiveTab('all')
  }

  const handleDeleteTemplate = async (template) => {
    if (!template?.id) return
    const name = template.name || template.id
    const confirmed = confirmDelete(`Delete "${name}"? This cannot be undone.`)
    if (!confirmed) return
    setDeleting(template.id)
    try {
      await deleteTemplateRequest(template.id)
      removeTemplate(template.id)
      setOutputFormats((prev) => {
        const next = { ...(prev || {}) }
        delete next[template.id]
        return next
      })
      if (selected.includes(template.id)) {
        onToggle(template.id)
      }
      queryClient.setQueryData(['templates', isMock], (prev) => {
        if (Array.isArray(prev)) {
          return prev.filter((item) => item?.id !== template.id)
        }
        if (prev && Array.isArray(prev.templates)) {
          return {
            ...prev,
            templates: prev.templates.filter((item) => item?.id !== template.id),
          }
        }
        return prev
      })
      const state = useAppStore.getState()
      savePersistedCache({
        connections: state.savedConnections,
        templates: state.templates,
        lastUsed: state.lastUsed,
      })
      toast.show(`Deleted "${name}"`, 'success')
    } catch (err) {
      toast.show(String(err), 'error')
    } finally {
      setDeleting(null)
    }
  }

  const handleImportTemplate = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const result = await importTemplateZip({ file, name: file.name.replace(/\.zip$/i, '') })
      toast.show(`Imported template "${result.name || result.template_id}"`, 'success')
      queryClient.invalidateQueries(['templates', isMock])
      queryClient.invalidateQueries(['template-catalog', isMock])
    } catch (err) {
      toast.show(`Import failed: ${err}`, 'error')
    } finally {
      setImporting(false)
      if (importInputRef.current) {
        importInputRef.current.value = ''
      }
    }
  }

  const handleExportTemplate = async (template) => {
    if (!template?.id) return
    setExporting(template.id)
    try {
      await exportTemplateZip(template.id)
      toast.show(`Exported "${template.name || template.id}"`, 'success')
    } catch (err) {
      toast.show(`Export failed: ${err}`, 'error')
    } finally {
      setExporting(null)
    }
  }

  const renderCompanyGrid = (list) => (
    <Grid container spacing={2.5}>
      {list.map((t) => {
        const selectedState = selected.includes(t.id)
        const type = getTemplateKind(t).toUpperCase()
        const fmt = outputFormats[t.id] || 'auto'
        const previewInfo = resolveTemplatePreviewUrl(t)
        const htmlPreview = previewInfo.url
        const previewKey = previewInfo.key || `${t.id}-preview`
        const thumbnailInfo = resolveTemplateThumbnailUrl(t)
        const imagePreview = !htmlPreview ? thumbnailInfo.url : null
        const generatorArtifacts = {
          sql: t.artifacts?.generator_sql_pack_url,
          schemas: t.artifacts?.generator_output_schemas_url,
          meta: t.artifacts?.generator_assets_url,
        }
        const generatorMeta = t.generator || {}
        const hasGeneratorAssets = Object.values(generatorArtifacts).some(Boolean)
        const needsUserFix = Array.isArray(generatorMeta.needsUserFix) ? generatorMeta.needsUserFix : []
        const generatorStatusLabel = generatorMeta.invalid ? 'Needs review' : 'Ready'
        const generatorStatusColor = generatorMeta.invalid ? 'warning' : 'success'
        let generatorUpdated = null
        if (generatorMeta.updatedAt) {
          const parsed = new Date(generatorMeta.updatedAt)
          generatorUpdated = Number.isNaN(parsed.getTime()) ? null : parsed.toLocaleString()
        }
        const assetHref = (url) => (url ? buildDownloadUrl(withBase(url)) : null)
        const generatorReady = hasGeneratorAssets && !generatorMeta.invalid && needsUserFix.length === 0
        const lastEditInfo = buildLastEditInfo(t.generator?.summary)
        const lastEditChipLabel = lastEditInfo?.chipLabel || 'Not edited yet'
        const lastEditChipColor = lastEditInfo?.color || 'default'
        const lastEditChipVariant = lastEditInfo?.variant || 'outlined'
        const handleCardToggle = () => {
          if (!selectedState) {
            if (!hasGeneratorAssets) {
              toast.show('Generate SQL & schema assets for this template before selecting it.', 'warning')
              return
            }
            if (!generatorReady) {
              const detail = needsUserFix.length ? `Resolve: ${needsUserFix.join(', ')}` : 'Generator assets need attention.'
              toast.show(detail, 'warning')
              return
            }
          }
          onToggle(t.id)
        }
        const handleCardKeyDown = (event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            handleCardToggle()
          }
        }

        return (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={t.id} sx={{ minWidth: 0 }}>
            <Card
              variant="outlined"
              sx={[
                {
                  position: 'relative',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column',
                  minHeight: 300,
                  transition: 'border-color 160ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 160ms cubic-bezier(0.22, 1, 0.36, 1)',
                },
                selectedState && {
                  borderColor: 'text.secondary',
                  boxShadow: `0 0 0 1px ${alpha(secondary.violet[500], 0.28)}`,
                },
              ]}
            >
              <Checkbox
                checked={selectedState}
                onChange={() => onToggle(t.id)}
                onClick={(event) => event.stopPropagation()}
                sx={{ position: 'absolute', top: 12, left: 12, zIndex: 1 }}
                aria-label={`Select ${t.name}`}
              />
              <Box role="button" tabIndex={0} onKeyDown={handleCardKeyDown} onClick={handleCardToggle} sx={{ height: '100%', cursor: 'pointer' }}>
                <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, height: '100%', flexGrow: 1 }}>
                  <Box
                    sx={{
                      minHeight: 180,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      overflow: 'hidden',
                      bgcolor: 'background.default',
                      p: 1,
                      aspectRatio: '210 / 297',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {htmlPreview ? (
                      <ScaledIframePreview
                        key={previewKey}
                        src={htmlPreview}
                        title={`${t.name} preview`}
                        sx={{ width: '100%', height: '100%' }}
                        frameAspectRatio="210 / 297"
                        pageShadow
                        pageBorderColor={alpha(neutral[900], 0.08)}
                        marginGuides={{ inset: 28, color: alpha(secondary.violet[500], 0.28) }}
                      />
                    ) : imagePreview ? (
                      <Box component="img" src={imagePreview} alt={`${t.name} preview`} loading="lazy" sx={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', display: 'block' }} />
                    ) : (
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}
                      >
                        No preview yet
                      </Typography>
                    )}
                  </Box>
                  <Stack spacing={0.75}>
                    {!!t.description && (
                      <Typography variant="caption" color="text.secondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {t.description}
                      </Typography>
                    )}
                    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
                      {(t.tags || []).slice(0, 3).map((tag) => <Chip key={tag} label={tag} size="small" />)}
                      {(t.tags || []).length > 3 && <Chip size="small" variant="outlined" label={`+${(t.tags || []).length - 3}`} />}
                    </Stack>
                    {hasGeneratorAssets && (
                      <Stack spacing={0.75} sx={{ mt: 1 }}>
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap', rowGap: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            SQL & schema assets - {generatorMeta.dialect || 'unknown'}
                          </Typography>
                          <Chip size="small" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} label={generatorStatusLabel} />
                          {!!needsUserFix.length && (
                            <Tooltip title={needsUserFix.join('\\n')}>
                              <Chip
                                size="small"
                                sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                                variant="outlined"
                                label={`${needsUserFix.length} fix${needsUserFix.length === 1 ? '' : 'es'}`}
                              />
                            </Tooltip>
                          )}
                          {generatorUpdated && (
                            <Typography variant="caption" color="text.secondary">
                              Updated {generatorUpdated}
                            </Typography>
                          )}
                        </Stack>
                        <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
                          {generatorArtifacts.sql && (
                            <Button
                              size="small"
                              variant="outlined"
                              component="a"
                              href={assetHref(generatorArtifacts.sql)}
                              target="_blank"
                              rel="noopener"
                              onClick={(e) => e.stopPropagation()}
                            >
                              SQL Pack
                            </Button>
                          )}
                          {generatorArtifacts.schemas && (
                            <Button
                              size="small"
                              variant="outlined"
                              component="a"
                              href={assetHref(generatorArtifacts.schemas)}
                              target="_blank"
                              rel="noopener"
                              onClick={(e) => e.stopPropagation()}
                            >
                              Output Schemas
                            </Button>
                          )}
                          {generatorArtifacts.meta && (
                            <Button
                              size="small"
                              variant="outlined"
                              component="a"
                              href={assetHref(generatorArtifacts.meta)}
                              target="_blank"
                              rel="noopener"
                              onClick={(e) => e.stopPropagation()}
                            >
                              Generator JSON
                            </Button>
                          )}
                        </Stack>
                      </Stack>
                    )}
                  </Stack>
                  <Divider sx={{ mt: 'auto', my: 1 }} />
                  <Stack spacing={1} alignItems="flex-start">
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, lineHeight: 1.2 }} noWrap>
                      {t.name}
                    </Typography>
                    <Stack
                      direction="row"
                      spacing={1}
                      alignItems="center"
                      sx={{ flexWrap: 'wrap', rowGap: 1 }}
                    >
                      <Chip size="small" label={type} variant="outlined" />
                      <Select
                        size="small"
                        value={fmt}
                        onChange={(e) => setOutputFormats((m) => ({ ...m, [t.id]: e.target.value }))}
                        onClick={(event) => event.stopPropagation()}
                        onMouseDown={(event) => event.stopPropagation()}
                        sx={{ bgcolor: 'background.paper', minWidth: 132 }}
                        aria-label="Output format"
                      >
                        <MenuItem value="auto">Auto ({type})</MenuItem>
                        <MenuItem value="pdf">PDF</MenuItem>
                        <MenuItem value="docx">Word (DOCX)</MenuItem>
                        <MenuItem value="xlsx">Excel (XLSX)</MenuItem>
                      </Select>
                      <Button
                        size="small"
                        variant={selectedState ? 'contained' : 'outlined'}
                        onClick={(e) => {
                          e.preventDefault()
                          e.stopPropagation()
                          handleCardToggle()
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                      >
                        {selectedState ? 'Selected' : 'Select'}
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        sx={{ color: 'text.secondary' }}
                        startIcon={
                          deleting === t.id ? (
                            <CircularProgress size={16} color="inherit" />
                          ) : (
                            <DeleteOutlineIcon fontSize="small" />
                          )
                        }
                        onClick={(e) => {
                          e.preventDefault()
                          e.stopPropagation()
                          handleDeleteTemplate(t)
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                        disabled={deleting === t.id}
                        aria-label={`Delete ${t.name || 'template'}`}
                      >
                        Delete
                      </Button>
                      {typeof onEditTemplate === 'function' && (
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<EditOutlinedIcon fontSize="small" />}
                        onClick={(e) => {
                          e.preventDefault()
                          e.stopPropagation()
                          onEditTemplate(t)
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                        aria-label={`Edit ${t.name || t.id}`}
                      >
                        Edit
                      </Button>
                    )}
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={
                          exporting === t.id ? (
                            <CircularProgress size={16} color="inherit" />
                          ) : (
                            <DownloadOutlinedIcon fontSize="small" />
                          )
                        }
                        onClick={(e) => {
                          e.preventDefault()
                          e.stopPropagation()
                          handleExportTemplate(t)
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                        disabled={exporting === t.id}
                        aria-label={`Export ${t.name || 'template'}`}
                      >
                        Export
                      </Button>
                      <Chip
                        size="small"
                        label={lastEditChipLabel}
                        color={lastEditInfo ? lastEditChipColor : 'default'}
                        variant={lastEditInfo ? lastEditChipVariant : 'outlined'}
                        sx={{ mt: 0.5 }}
                      />
                    </Stack>
                  </Stack>
                </CardContent>
              </Box>
            </Card>
          </Grid>
        )
      })}
    </Grid>
  )

  const renderStarterGrid = (list) => (
    <Grid container spacing={2.5}>
      {list.map((t) => (
        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={t.id} sx={{ minWidth: 0 }}>
          <Card variant="outlined">
            <CardContent>
              <Stack spacing={1}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {t.name || t.id}
                </Typography>
                {t.description && (
                  <Typography variant="body2" color="text.secondary">
                    {t.description}
                  </Typography>
                )}
                <Typography variant="caption" color="text.secondary">
                  Starter template - Read-only
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  )

  const renderRecommendations = () => {
    if (!recommendations.length) {
      return (
        <EmptyState
          size="medium"
          title="No recommendations yet"
          description="Describe what you need and click Get recommendations to see suggestions."
        />
      )
    }
    return (
      <Grid container spacing={2.5}>
        {recommendations.map((entry, index) => {
          const template = entry?.template || {}
          const meta = getSourceMeta(template.source)
          const isStarter = meta.isStarter
          return (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={template.id || `rec-${index}`} sx={{ minWidth: 0 }}>
              <Card variant="outlined">
                <CardContent>
                  <Stack spacing={1.25}>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap' }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {template.name || template.id || 'Template'}
                      </Typography>
                      <Chip size="small" label={meta.label} sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} variant={meta.variant} />
                    </Stack>
                    {template.description && (
                      <Typography variant="body2" color="text.secondary">
                        {template.description}
                      </Typography>
                    )}
                    {entry?.explanation && (
                      <Typography variant="body2">
                        {entry.explanation}
                      </Typography>
                    )}
                    <Typography variant="caption" color="text.secondary">
                      {isStarter ? 'Starter template - Review before use' : 'Company template - Editable'}
                    </Typography>
                    {!isStarter && (
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleFindInAll(template.name || template.id)}
                      >
                        Find in "All" templates
                      </Button>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>
    )
  }

  const renderAllTab = () => {
    const sections = []
    const hasCompanyTemplates = companyCandidates.length > 0
    const starterSectionList = showStarterInAll ? applyTagFilter(starterCandidates) : starterMatches
    const hasStarterTemplates = showStarterInAll && starterSectionList.length > 0
    if (hasCompanyTemplates) {
      sections.push(
        <Stack key="company" spacing={1.5}>
          <Typography variant="subtitle2">Company templates</Typography>
          {companyMatches.length ? (
            renderCompanyGrid(companyMatches)
          ) : (
            <Typography variant="body2" color="text.secondary">
              No company templates match the current filters.
            </Typography>
          )}
        </Stack>,
      )
    }
    if (hasStarterTemplates) {
      sections.push(
        <Stack key="starter" spacing={1.5}>
          <Typography variant="subtitle2">Starter templates</Typography>
          {starterSectionList.length ? (
            renderStarterGrid(starterSectionList)
          ) : (
            <Typography variant="body2" color="text.secondary">
              No starter templates match the current filters.
            </Typography>
          )}
        </Stack>,
      )
    }
    if (!sections.length) {
      return (
        <EmptyState
          size="medium"
          title="No templates match the current filters"
          description="Adjust the search text or tags to see more templates."
        />
      )
    }
    return <Stack spacing={3}>{sections}</Stack>
  }

  const renderCompanyTab = () => {
    if (!companyMatches.length) {
      return (
        <EmptyState
          size="medium"
          title="No company templates match"
          description="Try clearing the search text or adjusting the tag filters."
        />
      )
    }
    return renderCompanyGrid(companyMatches)
  }

  const renderStarterTab = () => {
    if (!starterMatches.length) {
      return (
        <EmptyState
          size="medium"
          title="No starter templates available"
          description="Starter templates will appear here when provided by the catalog."
        />
      )
    }
    return renderStarterGrid(starterMatches)
  }

  const renderRecommendedTab = () => renderRecommendations()

  const tabContent = () => {
    if (activeTab === 'company') return renderCompanyTab()
    if (activeTab === 'starter') return renderStarterTab()
    if (activeTab === 'recommended') return renderRecommendedTab()
    return renderAllTab()
  }

  const showRefreshing = (isFetching && !isLoading) || catalogQuery.isFetching

  return (
    <Surface sx={surfaceStackSx}>
      <Stack spacing={1.5}>
        <Stack direction="row" alignItems="center" spacing={0.75} justifyContent="space-between" flexWrap="wrap">
          <Stack direction="row" alignItems="center" spacing={0.75}>
            <Typography variant="h6">Template Picker</Typography>
            <InfoTooltip
              content={TOOLTIP_COPY.templatePicker}
              ariaLabel="Template picker guidance"
            />
          </Stack>
          <Stack direction="row" spacing={1}>
            <input
              type="file"
              accept=".zip"
              ref={importInputRef}
              onChange={handleImportTemplate}
              style={{ display: 'none' }}
              aria-label="Import template zip file"
            />
            <Button
              size="small"
              variant="outlined"
              startIcon={
                importing ? (
                  <CircularProgress size={16} color="inherit" />
                ) : (
                  <FileUploadOutlinedIcon fontSize="small" />
                )
              }
              onClick={() => importInputRef.current?.click()}
              disabled={importing}
            >
              {importing ? 'Importing...' : 'Import Template'}
            </Button>
          </Stack>
        </Stack>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} alignItems={{ xs: 'stretch', md: 'center' }}>
          <Autocomplete
            multiple
            options={allTags}
            value={tagFilter}
            onChange={(e, v) => setTagFilter(v)}
            freeSolo
            renderInput={(params) => <TextField {...params} label="Filter by tags" />}
            sx={{ maxWidth: 440 }}
          />
          <TextField
            label="Search by name"
            size="small"
            value={nameQuery}
            onChange={(e) => {
              const value = e.target.value
              setNameQuery(value)
              setShowStarterInAll(!value.trim())
            }}
            sx={{ maxWidth: 320 }}
          />
        </Stack>
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          spacing={1}
          alignItems={{ xs: 'stretch', md: 'center' }}
        >
          <TextField
            label="Describe what you need"
            size="small"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            onKeyDown={handleRequirementKeyDown}
            fullWidth
            id="template-recommendation-requirement"
            InputLabelProps={{ shrink: true }}
            inputProps={{ 'aria-label': 'Describe what you need' }}
          />
          <Autocomplete
            multiple
            options={kindOptions}
            value={kindHints}
            onChange={(_e, v) => setKindHints(v)}
            size="small"
            renderInput={(params) => <TextField {...params} label="Kinds (pdf/excel)" />}
            sx={{ minWidth: 200 }}
          />
          <Autocomplete
            multiple
            options={domainOptions}
            value={domainHints}
            onChange={(_e, v) => setDomainHints(v)}
            size="small"
            renderInput={(params) => <TextField {...params} label="Domains" />}
            sx={{ minWidth: 220 }}
          />
          <Button
            variant="contained"
            onClick={handleRecommend}
            disabled={recommending || queueingRecommendations}
            sx={{ whiteSpace: 'nowrap' }}
          >
            {recommending ? 'Finding...' : 'Get recommendations'}
          </Button>
          <Button
            variant="outlined"
            onClick={handleQueueRecommend}
            disabled={recommending || queueingRecommendations}
            startIcon={
              queueingRecommendations ? (
                <CircularProgress size={16} color="inherit" />
              ) : (
                <ScheduleIcon fontSize="small" />
              )
            }
            sx={{ whiteSpace: 'nowrap' }}
          >
            {queueingRecommendations ? 'Queueing...' : 'Queue'}
          </Button>
        </Stack>
      </Stack>
      <Collapse in={showRefreshing} unmountOnExit>
        <LinearProgress sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] }, borderRadius: 1 }} aria-label="Refreshing templates" />
      </Collapse>
      {isLoading ? (
        <LoadingState
          label="Loading approved templates..."
          description="Fetching the latest approved templates from the pipeline."
        />
      ) : isError ? (
        <Alert severity="error">
          {String(error?.message || 'Failed to load approved templates.')}
        </Alert>
      ) : (
        <>
          <Tabs
            value={activeTab}
            onChange={(event, value) => setActiveTab(value)}
            variant="scrollable"
            allowScrollButtonsMobile
          >
            <Tab label="All" value="all" />
            <Tab label="Company" value="company" />
            <Tab label="Starter" value="starter" />
            <Tab label="Recommended" value="recommended" />
          </Tabs>
          <Box sx={{ mt: 2 }}>{tabContent()}</Box>
        </>
      )}
    </Surface>
  )
}

export default TemplatePicker

