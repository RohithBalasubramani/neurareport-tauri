import { useCallback } from 'react'
import { Box, Typography, Stack, Chip, Alert } from '@mui/material'
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined'
import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'

const ACCEPTED_EXTENSIONS = '.pdf,.xls,.xlsx'
const EXCEL_MAX_DATA_ROWS = Number(import.meta.env?.VITE_EXCEL_MAX_DATA_ROWS ?? '30') || 30

export default function UploadDropzone({
  file,
  format,
  dropDisabled,
  inputRef,
  uploadInputId,
  dropDescriptionId,
  onPick,
  onDrop,
  hasInProgressSetupRef,
  applySelectedFile,
  setPendingFileAction,
}) {
  const handleDropzoneKey = useCallback((event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      inputRef.current?.click()
    }
  }, [inputRef])

  const handleDragOver = useCallback((event) => {
    event.preventDefault()
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'copy'
    }
  }, [])

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault()
      const fileList = event.dataTransfer?.files
      if (fileList?.length) {
        const dropped = fileList[0]
        if (hasInProgressSetupRef.current) {
          setPendingFileAction({ action: 'replace', file: dropped })
          return
        }
        applySelectedFile(dropped)
      }
    },
    [applySelectedFile, hasInProgressSetupRef, setPendingFileAction],
  )

  return (
    <Box sx={{ mt: 1.5, display: 'grid', gap: 1.5 }}>
      <Box
        role="button"
        tabIndex={dropDisabled ? -1 : 0}
        aria-describedby={dropDescriptionId}
        aria-disabled={dropDisabled}
        onClick={() => {
          if (!dropDisabled) inputRef.current?.click()
        }}
        onKeyDown={dropDisabled ? undefined : handleDropzoneKey}
        onDragOver={dropDisabled ? undefined : handleDragOver}
        onDrop={dropDisabled ? undefined : handleDrop}
        sx={{
          position: 'relative',
          borderRadius: 1,
          border: '1px dashed',
          borderColor: (theme) => {
            if (dropDisabled) return alpha(theme.palette.action.disabled, 0.4)
            if (file) return theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
            return alpha(theme.palette.divider, 0.5)
          },
          px: { xs: 2.5, sm: 3.5 },
          py: { xs: 3, sm: 3.5 },
          textAlign: 'center',
          outline: 'none',
          cursor: dropDisabled ? 'not-allowed' : 'pointer',
          bgcolor: (theme) => {
            if (dropDisabled) return alpha(theme.palette.action.disabledBackground, 0.4)
            if (file) return theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]
            return theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50]
          },
          color: 'text.secondary',
          transition: 'border-color 160ms cubic-bezier(0.22, 1, 0.36, 1), background-color 160ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 160ms cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': dropDisabled
            ? {}
            : {
                borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
              },
          '&:focus-visible': dropDisabled
            ? {}
            : {
                borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                boxShadow: (theme) => `0 0 0 3px ${alpha(theme.palette.text.primary, 0.1)}`,
              },
        }}
      >
        <Stack spacing={1.5} alignItems="center">
          <Box
            aria-hidden
            sx={{
              width: 48,
              height: 48,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'common.white',
              boxShadow: `0 8px 20px ${alpha(neutral[900], 0.12)}`,
              color: 'text.secondary',
            }}
          >
            <CloudUploadOutlinedIcon fontSize="medium" />
          </Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {dropDisabled ? 'Verification in progress...' : 'Drop design here or click to browse'}
          </Typography>
            <Typography id={dropDescriptionId} variant="body2" color="text.secondary">
              Accepts PDF or Excel files (.pdf, .xls, .xlsx)
            </Typography>
            {format === 'Excel' && (
              <Alert severity="info" sx={{ mt: 1, alignSelf: 'stretch' }}>
                Excel previews support up to {EXCEL_MAX_DATA_ROWS} data rows. Delete extra rows before uploading a new file.
              </Alert>
            )}
          <Stack direction="row" spacing={1}>
            <Chip label="PDF" size="small" variant="outlined" />
            <Chip label="Excel" size="small" variant="outlined" />
          </Stack>
        </Stack>
        <input
          ref={inputRef}
          id={uploadInputId}
          type="file"
          hidden
          accept={ACCEPTED_EXTENSIONS}
          onChange={onPick}
          disabled={dropDisabled}
        />
      </Box>
    </Box>
  )
}
