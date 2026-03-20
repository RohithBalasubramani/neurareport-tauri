import { Box, Stack, Typography, IconButton } from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'

export default function ChatHeader({ mode, onClearChat }) {
  return (
    <Box
      sx={{
        p: 2,
        borderBottom: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="subtitle1" fontWeight={600}>
            {mode === 'create' ? 'AI Template Creator' : 'AI Template Editor'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {mode === 'create'
              ? 'Describe the report you need and I\'ll build it for you'
              : 'Describe the changes you want and I\'ll help you implement them'}
          </Typography>
        </Box>
        <IconButton
          size="small"
          onClick={onClearChat}
          title="Clear chat and start over"
        >
          <RefreshIcon fontSize="small" />
        </IconButton>
      </Stack>
    </Box>
  )
}
