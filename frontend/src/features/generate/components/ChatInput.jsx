import {
  Box,
  Stack,
  Typography,
  TextField,
  IconButton,
  CircularProgress,
  alpha,
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import { neutral } from '@/app/theme'

export default function ChatInput({
  inputRef,
  inputValue,
  onInputChange,
  onKeyDown,
  onSend,
  isProcessing,
  readyToApply,
  placeholder,
}) {
  return (
    <Box
      sx={{
        p: 2,
        borderTop: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          gap: 1,
          p: 1.5,
          borderRadius: 1,  // Figma spec: 8px
          bgcolor: (theme) => alpha(theme.palette.action.hover, 0.5),
          border: 1,
          borderColor: 'divider',
          transition: 'all 150ms cubic-bezier(0.22, 1, 0.36, 1)',
          '&:focus-within': {
            borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
            boxShadow: (theme) =>
              `0 0 0 2px ${alpha(theme.palette.text.primary, 0.08)}`,
          },
        }}
      >
        <TextField
          inputRef={inputRef}
          fullWidth
          multiline
          maxRows={4}
          placeholder={
            isProcessing
              ? 'Processing...'
              : readyToApply
              ? 'Apply the changes above or describe different modifications...'
              : placeholder
          }
          value={inputValue}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={isProcessing}
          variant="standard"
          InputProps={{
            disableUnderline: true,
            sx: {
              fontSize: '1rem',
              lineHeight: 1.5,
            },
          }}
          sx={{
            '& .MuiInputBase-root': {
              py: 0.5,
            },
          }}
        />

        <IconButton
          onClick={onSend}
          disabled={!inputValue.trim() || isProcessing}
          sx={{
            bgcolor: (theme) => inputValue.trim() && !isProcessing
              ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
              : 'action.disabledBackground',
            color: inputValue.trim() && !isProcessing
              ? 'common.white'
              : 'text.disabled',
            '&:hover': {
              bgcolor: (theme) => inputValue.trim() && !isProcessing
                ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
                : 'action.disabledBackground',
            },
          }}
        >
          {isProcessing ? (
            <CircularProgress size={20} color="inherit" />
          ) : (
            <SendIcon fontSize="small" />
          )}
        </IconButton>
      </Box>

      <Stack
        direction="row"
        spacing={2}
        justifyContent="center"
        sx={{ mt: 1 }}
      >
        <Typography variant="caption" color="text.disabled">
          Press Enter to send, Shift+Enter for new line
        </Typography>
      </Stack>
    </Box>
  )
}
