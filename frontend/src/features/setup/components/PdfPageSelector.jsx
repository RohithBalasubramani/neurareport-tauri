import { Typography, Stack, Button } from '@mui/material'
import { alpha } from '@mui/material/styles'

export default function PdfPageSelector({
  file,
  format,
  pageCount,
  selectedPage,
  setSelectedPage,
  verifying,
}) {
  if (!file || format !== 'PDF' || pageCount <= 1) return null
  return (
    <Stack
      direction="row"
      spacing={1.5}
      alignItems="center"
      sx={{
        mt: 1.5,
        px: 2,
        py: 1,
        borderRadius: 1,
        border: '1px solid',
        borderColor: 'divider',
        bgcolor: (theme) => theme.palette.mode === 'dark'
          ? alpha(theme.palette.info.main, 0.08)
          : alpha(theme.palette.info.main, 0.06),
      }}
    >
      <Typography variant="body2" sx={{ fontWeight: 500 }}>
        This PDF has {pageCount} pages. Select the page to verify:
      </Typography>
      <Stack direction="row" spacing={0.5} alignItems="center">
        <Button
          size="small"
          variant="outlined"
          disabled={selectedPage <= 0 || verifying}
          onClick={() => setSelectedPage((p) => Math.max(0, p - 1))}
          sx={{ minWidth: 32, px: 0.5 }}
        >
          &lsaquo;
        </Button>
        <Typography
          variant="body2"
          sx={{ minWidth: 60, textAlign: 'center', fontWeight: 600 }}
        >
          Page {selectedPage + 1} / {pageCount}
        </Typography>
        <Button
          size="small"
          variant="outlined"
          disabled={selectedPage >= pageCount - 1 || verifying}
          onClick={() => setSelectedPage((p) => Math.min(pageCount - 1, p + 1))}
          sx={{ minWidth: 32, px: 0.5 }}
        >
          &rsaquo;
        </Button>
      </Stack>
    </Stack>
  )
}
