import {
  Box, Typography, Stack, Button, Chip, Divider,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import { neutral, secondary } from '@/app/theme'
import ReplayIcon from '@mui/icons-material/Replay'
import { withBase } from '@/api/client'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import Surface from '@/components/layout/Surface.jsx'
import { buildDownloadUrl, surfaceStackSx } from '../utils/templatesPaneUtils'

export default function RecentDownloadsSection({ downloads }) {
  return (
    <Surface sx={surfaceStackSx}>
      <Stack direction="row" alignItems="center" spacing={0.75}>
        <Typography variant="h6">Recently Downloaded</Typography>
        <InfoTooltip
          content={TOOLTIP_COPY.recentDownloads}
          ariaLabel="How to use recent downloads"
        />
      </Stack>
      <Stack spacing={1.5}>
        {downloads.map((d, i) => {
          const metaLine = [d.template, d.format ? d.format.toUpperCase() : null, d.size || 'Size unknown']
            .filter(Boolean)
            .join(' \u2022 ')
          const formatChips = [
            d.pdfUrl && { label: 'PDF', color: 'primary' },
            d.docxUrl && { label: 'DOCX', color: 'secondary' },
            d.xlsxUrl && { label: 'XLSX', color: 'info' },
          ].filter(Boolean)
          const actionButtons = [
            {
              key: 'open',
              label: 'Open preview',
              variant: 'outlined',
              color: 'inherit',
              disabled: !d.htmlUrl,
              href: d.htmlUrl ? withBase(d.htmlUrl) : null,
            },
            {
              key: 'pdf',
              label: 'Download PDF',
              variant: 'contained',
              color: 'primary',
              disabled: !d.pdfUrl,
              href: d.pdfUrl ? buildDownloadUrl(withBase(d.pdfUrl)) : null,
            },
            d.docxUrl && {
              key: 'docx',
              label: 'Download DOCX',
              variant: 'outlined',
              color: 'primary',
              href: buildDownloadUrl(withBase(d.docxUrl)),
            },
            d.xlsxUrl && {
              key: 'xlsx',
              label: 'Download XLSX',
              variant: 'outlined',
              color: 'info',
              href: buildDownloadUrl(withBase(d.xlsxUrl)),
            },
          ].filter(Boolean)
          return (
            <Box
              key={`${d.filename}-${i}`}
              sx={{
                p: { xs: 1.5, md: 2 },
                borderRadius: 1,  // Figma spec: 8px
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.paper',
                boxShadow: `0 6px 20px ${alpha(neutral[900], 0.06)}`,
                transition: 'border-color 200ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 200ms cubic-bezier(0.22, 1, 0.36, 1), transform 160ms cubic-bezier(0.22, 1, 0.36, 1)',
                '&:hover': {
                  borderColor: 'primary.light',
                  boxShadow: `0 10px 30px ${alpha(secondary.violet[500], 0.14)}`,
                  transform: 'translateY(-2px)',
                },
              }}
            >
              <Stack spacing={1.5}>
                <Stack
                  direction={{ xs: 'column', md: 'row' }}
                  spacing={1}
                  justifyContent="space-between"
                  alignItems={{ md: 'center' }}
                >
                  <Box sx={{ minWidth: 0 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }} noWrap title={d.filename}>
                      {d.filename}
                    </Typography>
                    {metaLine && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 0.5 }}
                        noWrap
                        title={metaLine}
                      >
                        {metaLine}
                      </Typography>
                    )}
                  </Box>
                  {!!formatChips.length && (
                    <Stack direction="row" spacing={0.75} flexWrap="wrap" justifyContent={{ xs: 'flex-start', md: 'flex-end' }}>
                      {formatChips.map(({ label, color: colorKey }) => (
                        <Chip
                          key={label}
                          size="small"
                          label={label}
                          sx={(theme) => ({
                            borderRadius: 1,
                            fontWeight: 600,
                            bgcolor: alpha(theme.palette[colorKey].main, 0.12),
                            color: theme.palette[colorKey].dark,
                            border: '1px solid',
                            borderColor: alpha(theme.palette[colorKey].main, 0.3),
                          })}
                        />
                      ))}
                    </Stack>
                  )}
                </Stack>

                <Divider />

                <Stack
                  direction={{ xs: 'column', lg: 'row' }}
                  spacing={1.25}
                  alignItems={{ lg: 'flex-start' }}
                >
                  <Stack
                    direction="row"
                    spacing={1}
                    flexWrap="wrap"
                    sx={{ flexGrow: 1, columnGap: 1, rowGap: 1 }}
                  >
                    {actionButtons.map((action) => {
                      const linkProps = action.href
                        ? { component: 'a', href: action.href, target: '_blank', rel: 'noopener' }
                        : {}
                      return (
                        <Button
                          key={action.key}
                          size="small"
                          variant={action.variant}
                          color={action.color}
                          disabled={action.disabled}
                          sx={{
                            textTransform: 'none',
                            minWidth: { xs: '100%', sm: 0 },
                            flex: { xs: '1 1 100%', sm: '0 0 auto' },
                            px: 2.5,
                          }}
                          {...linkProps}
                        >
                          {action.label}
                        </Button>
                      )
                    })}
                  </Stack>
                  <Box sx={{ width: { xs: '100%', lg: 'auto' } }}>
                    <Button
                      size="small"
                      variant="contained"
                      disableElevation
                      startIcon={<ReplayIcon />}
                      onClick={d.onRerun}
                      sx={{ width: { xs: '100%', lg: 'auto' }, textTransform: 'none', px: 2.5, bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
                    >
                      Re-run
                    </Button>
                  </Box>
                </Stack>
              </Stack>
            </Box>
          )
        })}
        {!downloads.length && <Typography variant="body2" color="text.secondary">No recent downloads yet.</Typography>}
      </Stack>
    </Surface>
  )
}
