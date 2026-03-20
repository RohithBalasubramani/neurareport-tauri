import { Box, Stack, Typography, Chip } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'

export default function ResponseSection({ lastResponse, responseBody }) {
  return (
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
  )
}
