import { Box, Stack, Typography, alpha } from '@mui/material'
import PersonOutlineIcon from '@mui/icons-material/PersonOutline'
import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined'
import { neutral } from '@/app/theme'

const ROLE_CONFIG = {
  user: {
    icon: PersonOutlineIcon,
    label: 'You',
    bgcolor: neutral[900],
    textColor: 'common.white',
  },
  assistant: {
    icon: SmartToyOutlinedIcon,
    label: 'NeuraReport',
    bgcolor: 'background.paper',
    textColor: 'text.primary',
  },
}

export default function ChatMessage({ message }) {
  const { role, content, timestamp } = message
  const config = ROLE_CONFIG[role] || ROLE_CONFIG.assistant
  const Icon = config.icon
  const isUser = role === 'user'

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: 1.5,
        px: 2,
        py: 1.5,
      }}
    >
      <Box
        sx={{
          width: 32,
          height: 32,
          borderRadius: '50%',
          bgcolor: isUser ? neutral[900] : neutral[500],
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <Icon sx={{ fontSize: 18, color: 'white' }} />
      </Box>

      <Box
        sx={{
          flex: 1,
          maxWidth: isUser ? 'calc(100% - 100px)' : 'calc(100% - 48px)',
          minWidth: 0,
        }}
      >
        <Stack
          direction="row"
          spacing={1}
          alignItems="center"
          sx={{
            mb: 0.5,
            justifyContent: isUser ? 'flex-end' : 'flex-start',
          }}
        >
          <Typography variant="caption" fontWeight={600} color="text.primary">
            {config.label}
          </Typography>
          {timestamp && (
            <Typography variant="caption" color="text.disabled">
              {new Date(timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Typography>
          )}
        </Stack>

        <Box
          sx={{
            p: 2,
            borderRadius: 1,  // Figma spec: 8px
            bgcolor: isUser
              ? neutral[900]
              : 'background.paper',
            color: isUser ? 'common.white' : 'text.primary',
            boxShadow: isUser
              ? `0 2px 8px ${alpha(neutral[900], 0.2)}`
              : '0 1px 3px rgba(0,0,0,0.08)',
          }}
        >
          <Typography
            variant="body2"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              lineHeight: 1.6,
            }}
          >
            {content}
            {message.streaming && (
              <Box
                component="span"
                sx={{
                  display: 'inline-block',
                  width: 6,
                  height: 16,
                  ml: 0.5,
                  bgcolor: 'currentColor',
                  animation: 'blink 1s steps(1) infinite',
                  '@keyframes blink': {
                    '50%': { opacity: 0 },
                  },
                }}
              />
            )}
          </Typography>
        </Box>
      </Box>
    </Box>
  )
}
