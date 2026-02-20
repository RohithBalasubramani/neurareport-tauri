import Grid from '@mui/material/Grid2'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  alpha,
  Box, Typography, Stack, Button, TextField, Chip, Divider, LinearProgress,
  Card, CardActionArea, CardActions, CardContent, Autocomplete, Tooltip, Dialog, DialogContent, DialogTitle,
  CircularProgress, Alert, IconButton, Collapse,
} from '@mui/material'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  isMock,
  listApprovedTemplates,
  deleteTemplate as deleteTemplateRequest,
  importTemplateZip,
  templateExportZipUrl,
} from '@/api/client'
import * as mock from '@/api/mock'
import { savePersistedCache } from '@/hooks/useBootstrapState.js'
import { useAppStore } from '@/stores'
import { confirmDelete } from '@/utils/confirmDelete'
import { useToast } from '@/components/ToastProvider.jsx'
import Surface from '@/components/layout/Surface.jsx'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'
import { resolveTemplatePreviewUrl, resolveTemplateThumbnailUrl } from '@/utils/preview'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import LoadingState from '@/components/feedback/LoadingState.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { getTemplateKind, previewFrameSx, surfaceStackSx } from '../utils/templatesPaneUtils'
import { neutral, palette, secondary } from '@/app/theme'

function TemplatePicker({ selected, onToggle, tagFilter, setTagFilter }) {

  const { templates, setTemplates, removeTemplate, setSetupNav } = useAppStore()

  const toast = useToast()

  const queryClient = useQueryClient()

  const [deleting, setDeleting] = useState(null)

  const [importing, setImporting] = useState(false)

  const [nameQuery, setNameQuery] = useState('')

  const fileInputRef = useRef(null)

  const [previewOpen, setPreviewOpen] = useState(false)

  const [previewSrc, setPreviewSrc] = useState(null)

  const [previewType, setPreviewType] = useState('html')

  const [previewKey, setPreviewKey] = useState(null)

  const { data, isLoading, isFetching } = useQuery({

    queryKey: ['templates'],

    queryFn: () => (isMock ? mock.listTemplates() : listApprovedTemplates()),

  })



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



  const approved = useMemo(() => templates.filter((t) => t.status === 'approved'), [templates])

  const allTags = useMemo(() => Array.from(new Set(approved.flatMap((t) => t.tags || []))), [approved])

  const filtered = useMemo(() => {

    const tagFiltered = tagFilter.length

      ? approved.filter((t) => (t.tags || []).some((tag) => tagFilter.includes(tag)))

      : approved

    const nq = nameQuery.trim().toLowerCase()

    return nq ? tagFiltered.filter((t) => (t.name || '').toLowerCase().includes(nq)) : tagFiltered

  }, [approved, tagFilter, nameQuery])



  const handleImportFile = useCallback(

    async (file) => {

      if (!file) return

      if (isMock) {

        toast.show('Import is unavailable while using mock data.', 'info')

        return

      }

      setImporting(true)

      try {

        const baseName = file.name ? file.name.replace(/\.zip$/i, '').trim() : ''

        const result = await importTemplateZip({ file, name: baseName || undefined })

        await queryClient.invalidateQueries({ queryKey: ['templates'] })

        toast.show(`Imported "${result?.name || baseName || file.name}"`, 'success')

      } catch (err) {

        toast.show(String(err), 'error')

      } finally {

        setImporting(false)

        if (fileInputRef.current) {

          fileInputRef.current.value = ''

        }

      }

    },

    [toast, queryClient],

  )



  const handleImportClick = useCallback(() => {

    if (isMock) {

      toast.show('Import is unavailable while using mock data.', 'info')

      return

    }

    fileInputRef.current?.click()

  }, [toast])



  const handleImportInputChange = useCallback(

    (event) => {

      const nextFile = event?.target?.files?.[0]

      if (nextFile) {

        handleImportFile(nextFile)

      }

    },

    [handleImportFile],

  )



  const handleThumbClick = (event, payload) => {

    event.stopPropagation()

    const url = payload?.url

    if (!url) return

    setPreviewSrc(url)

    setPreviewType(payload?.type || 'html')

    setPreviewKey(payload?.key || url)

    setPreviewOpen(true)

  }



  const handlePreviewClose = () => {

    setPreviewOpen(false)

    setPreviewSrc(null)

    setPreviewType('html')

    setPreviewKey(null)

  }



  const handleDeleteTemplate = async (template) => {

    if (!template?.id) return

    const name = template.name || template.id

    if (typeof window !== 'undefined') {

      const confirmed = confirmDelete(`Delete template "${name}"? This action cannot be undone.`)

      if (!confirmed) return

    }

    setDeleting(template.id)

    try {

      await deleteTemplateRequest(template.id)

      removeTemplate(template.id)

      if (selected.includes(template.id)) {

        onToggle(template.id)

      }

      queryClient.setQueryData(['templates'], (prev) => {

        if (Array.isArray(prev)) {

          return prev.filter((tpl) => tpl?.id !== template.id)

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



  let templateListContent

  if (!templates.length && (isLoading || isFetching)) {

    templateListContent = (

      <Box sx={{ py: 6, display: 'flex', justifyContent: 'center' }}>

        <LoadingState label="Loading templates..." description="Fetching approved templates from the server." />

      </Box>

    )

  } else if (!filtered.length) {

    templateListContent = (

      <EmptyState

        title={tagFilter.length || nameQuery.trim() ? 'No templates match the filters' : 'No approved templates yet'}

        description={tagFilter.length || nameQuery.trim()

          ? 'Adjust the filters or clear them to see all approved templates.'

          : 'Upload and verify a template to make it available for runs.'}

        action={

          !filtered.length && !templates.length ? (

            <Button variant="contained" onClick={() => setSetupNav('generate')}>

              Upload template

            </Button>

          ) : null

        }

      />

    )

  } else {

    templateListContent = (

      <Grid container spacing={2}>

        {filtered.map((t) => {

          const selectedState = selected.includes(t.id)

          const type = getTemplateKind(t).toUpperCase()

          const previewInfo = resolveTemplatePreviewUrl(t)

          const thumbnailInfo = resolveTemplateThumbnailUrl(t)

          const htmlPreview = previewInfo.url

          const imagePreview = !htmlPreview ? thumbnailInfo.url : null

          const boxClickable = Boolean(htmlPreview || imagePreview)

          const mappingKeyCount = Array.isArray(t?.mappingKeys) ? t.mappingKeys.length : 0

          const exportHref = isMock ? null : templateExportZipUrl(t.id)

          return (

            <Grid size={{ xs: 12, sm: 6, md: 6 }} key={t.id} sx={{ minWidth: 0 }}>

              <Card

                variant="outlined"

                sx={[

                  {

                    position: 'relative',

                    overflow: 'hidden',

                    display: 'flex',

                    flexDirection: 'column',

                    minHeight: 280,

                    transition: 'border-color 160ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 160ms cubic-bezier(0.22, 1, 0.36, 1)',

                  },

                  selectedState && {

                    borderColor: 'text.secondary',

                    boxShadow: `0 0 0 1px ${alpha(secondary.violet[500], 0.28)}`,

                  },

                ]}

              >

                <CardActionArea component="div" onClick={() => onToggle(t.id)} sx={{ height: '100%' }}>

                  <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, height: '100%', flexGrow: 1 }}>

                    <Box

                      sx={[previewFrameSx, boxClickable && { cursor: 'pointer' }]}

                      onClick={(e) => {

                        if (htmlPreview) {

                          handleThumbClick(e, { url: htmlPreview, key: previewInfo.key, type: 'html' })

                        } else if (imagePreview) {

                          handleThumbClick(e, { url: imagePreview, key: imagePreview, type: 'image' })

                        }

                      }}

                    >

                      {htmlPreview ? (

                        <ScaledIframePreview

                          key={previewInfo.key}

                          src={htmlPreview}

                          title={`${t.name} preview`}

                          sx={{ width: '100%', height: '100%' }}

                          frameAspectRatio="210 / 297"

                        />

                      ) : imagePreview ? (

                        <img

                          src={imagePreview}

                          alt={`${t.name} preview`}

                          loading="lazy"

                          style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block', cursor: 'inherit' }}

                        />

                      ) : (

                        <Typography variant="caption" color="text.secondary" sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>

                          No preview yet

                        </Typography>

                      )}

                    </Box>



                    {!!t.description && (

                      <Typography variant="caption" color="text.secondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>

                        {t.description}

                      </Typography>

                    )}

                    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>

                      {(t.tags || []).slice(0, 4).map((tag) => (

                        <Chip key={tag} label={tag} size="small" />

                      ))}

                      {!!(t.tags || []).slice(4).length && <Chip size="small" label={`+${(t.tags || []).length - 4}`} variant="outlined" />}

                    </Stack>

                    <Divider sx={{ mt: 'auto', my: 1 }} />

                    <Stack spacing={1} alignItems="flex-start">

                      <Typography variant="subtitle1" sx={{ fontWeight: 600, lineHeight: 1.2 }} noWrap>

                        {t.name}

                      </Typography>

                      <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap', rowGap: 1 }}>

                        <Chip size="small" label={type} variant="outlined" />

                        {mappingKeyCount > 0 && (

                          <Chip

                            size="small"

                            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}

                            variant="outlined"

                            label={`${mappingKeyCount} key ${mappingKeyCount === 1 ? 'filter' : 'filters'}`}

                          />

                        )}

                      </Stack>

                    </Stack>

                  </CardContent>

                </CardActionArea>

                <CardActions

                  sx={{

                    justifyContent: 'space-between',

                    alignItems: 'center',

                    px: 2,

                    pb: 2,

                    gap: 1,

                    flexWrap: 'wrap',

                  }}

                >

                  <Button

                    size="small"

                    variant={selectedState ? 'contained' : 'outlined'}

                    onClick={(e) => {

                      e.preventDefault()

                      e.stopPropagation()

                      onToggle(t.id)

                    }}

                    startIcon={selectedState ? <CheckRoundedIcon fontSize="small" /> : undefined}

                  >

                    {selectedState ? 'Selected' : 'Select'}

                  </Button>

                  <Stack direction="row" spacing={0.5} alignItems="center">

                    <Tooltip title={exportHref ? 'Export template ZIP' : 'Export unavailable in mock mode'}>

                      <span>

                        <IconButton

                          size="small"

                          component={exportHref ? 'a' : 'button'}

                          href={exportHref || undefined}

                          target={exportHref ? '_blank' : undefined}

                          rel={exportHref ? 'noopener' : undefined}

                          onClick={(e) => {

                            if (!exportHref) e.preventDefault()

                            e.stopPropagation()

                          }}

                        >

                          <Inventory2OutlinedIcon fontSize="small" />

                        </IconButton>

                      </span>

                    </Tooltip>

                    <Tooltip title="Delete template">

                      <span>

                        <IconButton

                          size="small"

                          sx={{ color: 'text.secondary' }}

                          disabled={deleting === t.id}

                          onClick={(e) => {

                            e.preventDefault()

                            e.stopPropagation()

                            handleDeleteTemplate(t)

                          }}

                        >

                          {deleting === t.id ? (

                            <CircularProgress size={16} color="inherit" />

                          ) : (

                            <DeleteOutlineIcon fontSize="small" />

                          )}

                        </IconButton>

                      </span>

                    </Tooltip>

                  </Stack>

                </CardActions>

              </Card>

            </Grid>

          )

        })}

      </Grid>

    )

  }



  return (

    <Surface sx={surfaceStackSx}>

      <Stack spacing={1.5}>
        <Stack direction="row" alignItems="center" spacing={0.75}>
          <Typography variant="h6">Select Templates</Typography>
          <InfoTooltip content={TOOLTIP_COPY.templatePicker} ariaLabel="How to select templates" />
        </Stack>
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          spacing={1}
          alignItems={{ xs: 'flex-start', md: 'center' }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
            Export from any template card to download the entire uploads folder. Import the ZIP here to restore it on this device.
          </Typography>
          <Stack direction="row" spacing={1}>
            <Chip size="small" variant="outlined" label={`${selected.length} selected`} />
            <Chip size="small" variant="outlined" label={`${filtered.length} showing`} />
          </Stack>
        </Stack>
      </Stack>
      <Grid container spacing={1.5} alignItems="center" sx={{ pb: 1 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Autocomplete
            multiple
            options={allTags}
            value={tagFilter}
            onChange={(e, v) => setTagFilter(v)}
            freeSolo
            renderInput={(params) => <TextField {...params} label="Filter by tags" />}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <TextField
            label="Search by name"
            value={nameQuery}
            onChange={(e) => setNameQuery(e.target.value)}
            fullWidth
          />
        </Grid>
        <Grid
          size={{ xs: 12, md: 4 }}
          sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            style={{ display: 'none' }}
            onChange={handleImportInputChange}
          />
          <Tooltip title="Import an exported template bundle">
            <span>
              <Button
                variant="contained"
                startIcon={<UploadFileIcon />}
                onClick={handleImportClick}
                disabled={importing}
              >
                {importing ? 'Importing...' : 'Import Template'}
              </Button>
            </span>
          </Tooltip>
        </Grid>
      </Grid>
      <Collapse in={isFetching && !isLoading} unmountOnExit>

        <LinearProgress sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] }, borderRadius: 1 }} aria-label="Refreshing templates" />

      </Collapse>

      {templateListContent}

      <Dialog

        open={previewOpen}

        onClose={handlePreviewClose}

        maxWidth="lg"

        fullWidth

        aria-labelledby="template-preview-title"

        PaperProps={{

          sx: {

            height: '90vh',

            bgcolor: 'background.default',

          },

        }}

      >

        <DialogTitle id="template-preview-title">Template Preview</DialogTitle>

        <DialogContent

          dividers

          sx={{

            display: 'flex',

            justifyContent: 'center',

            alignItems: 'flex-start',

            overflow: 'auto',

            bgcolor: 'background.default',

          }}

        >

          {previewSrc && previewType === 'html' ? (

            <Box

              sx={{

                width: '100%',

                maxWidth: 1120,

                mx: 'auto',

                bgcolor: 'background.paper',

                borderRadius: 1,

                boxShadow: 2,

                border: '1px solid',

                borderColor: 'divider',

                overflow: 'auto',

                p: 2,

              }}

            >

              <ScaledIframePreview key={previewKey || previewSrc} src={previewSrc} title="Template HTML preview" sx={{ width: '100%', height: '100%' }} loading="eager" />

            </Box>

          ) : previewSrc ? (

            <Box

              component="img"

              src={previewSrc}

              alt="Template preview"

              sx={{

                display: 'block',

                width: '100%',

                maxWidth: 1120,

                height: 'auto',

                mx: 'auto',

                borderRadius: 1,

                boxShadow: 2,

              }}

            />

          ) : null}

        </DialogContent>

      </Dialog>

    </Surface>

  )

}

export default TemplatePicker
