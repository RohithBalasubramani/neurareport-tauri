import {
  Box, Typography, Stack, Button, LinearProgress,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import DownloadIcon from '@mui/icons-material/Download'
import FolderOpenIcon from '@mui/icons-material/FolderOpen'
import ReplayIcon from '@mui/icons-material/Replay'
import { buildDownloadUrl } from '../utils/templatesPaneUtils'

export default function ProgressList({ generation, onRetryGeneration }) {
  return (
    <Box>
      <Typography variant="subtitle1">Progress</Typography>
      <Stack spacing={1.5} sx={{ mt: 1.5 }}>
        {generation.items.map((item) => (
          <Box
            key={item.id}
            sx={{
              p: 1.5,
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1,
              bgcolor: 'background.paper',
            }}
          >
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              justifyContent="space-between"
              alignItems={{ xs: 'flex-start', sm: 'center' }}
              spacing={{ xs: 0.5, sm: 1 }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {item.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {item.status}
              </Typography>
            </Stack>
            <LinearProgress variant="determinate" value={item.progress} sx={{ mt: 1 }} />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }}>
              <Button
                size="small"
                variant="outlined"
                startIcon={<OpenInNewIcon />}
                disabled={!item.htmlUrl}
                component="a"
                href={item.htmlUrl || '#'}
                target="_blank"
                rel="noopener"
              >
                Open
              </Button>
              <Button
                size="small"
                variant="contained"
                disableElevation
                startIcon={<DownloadIcon />}
                disabled={!item.pdfUrl}
                component="a"
                href={item.pdfUrl ? buildDownloadUrl(item.pdfUrl) : '#'}
                target="_blank"
                rel="noopener"
                sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
              >
                Download
              </Button>
              {item.docxUrl && (
                <Button
                  size="small"
                  variant="contained"
                  disableElevation
                  startIcon={<DownloadIcon />}
                  component="a"
                  href={buildDownloadUrl(item.docxUrl)}
                  target="_blank"
                  rel="noopener"
                  sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[500] } }}
                >
                  Download DOCX
                </Button>
              )}
              {item.xlsxUrl && (
                <Button
                  size="small"
                  variant="contained"
                  disableElevation
                  startIcon={<DownloadIcon />}
                  component="a"
                  href={buildDownloadUrl(item.xlsxUrl)}
                  target="_blank"
                  rel="noopener"
                  sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[500], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[300] : neutral[500] } }}
                >
                  Download XLSX
                </Button>
              )}
              <Button size="small" variant="text" startIcon={<FolderOpenIcon />} disabled>
                Show in folder
              </Button>
              {item.status === 'failed' && (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<ReplayIcon />}
                  onClick={() => onRetryGeneration(item)}
                  sx={{ color: 'text.secondary', borderColor: (theme) => alpha(theme.palette.text.secondary, 0.3) }}
                >
                  Retry
                </Button>
              )}
            </Stack>
          </Box>
        ))}
        {!generation.items.length && <Typography variant="body2" color="text.secondary">No runs yet</Typography>}
      </Stack>
    </Box>
  )
}
