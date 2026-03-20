import {
  Box,
  Typography,
  Button,
  Stack,
  Chip,
  CircularProgress,
  LinearProgress,
  Avatar,
  alpha,
} from '@mui/material'
import { float } from '@/styles'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import BoltIcon from '@mui/icons-material/Bolt'
import { neutral } from '@/app/theme'

export function UploadPlaceholder({ theme }) {
  return (
    <Box>
      <Avatar
        sx={{
          width: 100,
          height: 100,
          mx: 'auto',
          mb: 3,
          background: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
          animation: `${float} 3s ease-in-out infinite`,
        }}
      >
        <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
      </Avatar>
      <Typography variant="h5" fontWeight={600} gutterBottom>
        Drop your document here
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
        or click to browse files
      </Typography>
      <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap">
        {['PDF', 'Excel', 'CSV', 'Word', 'Images'].map((type) => (
          <Chip
            key={type}
            label={type}
            size="small"
            sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100] }}
          />
        ))}
      </Stack>
    </Box>
  )
}

export function FileReady({ file, theme, onAnalyze }) {
  return (
    <Box>
      <Avatar
        sx={{
          width: 80,
          height: 80,
          mx: 'auto',
          mb: 3,
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
        }}
      >
        <CheckCircleIcon sx={{ fontSize: 40, color: 'text.secondary' }} />
      </Avatar>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        {file.name}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {(file.size / 1024 / 1024).toFixed(2)} MB
      </Typography>
      <Button
        variant="contained"
        size="large"
        onClick={(e) => {
          e.stopPropagation()
          onAnalyze()
        }}
        startIcon={<BoltIcon />}
        sx={{
          px: 6,
          py: 2,
          borderRadius: 1,  // Figma spec: 8px
          fontWeight: 600,
          fontSize: '1.1rem',
          textTransform: 'none',
          bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
          boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}`,
          transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': {
            transform: 'scale(1.05)',
            bgcolor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
            boxShadow: `0 12px 40px ${alpha(theme.palette.common.black, 0.25)}`,
          },
        }}
      >
        Analyze with AI
      </Button>
    </Box>
  )
}

export function AnalyzingProgress({ theme, progress, stage, onCancel }) {
  return (
    <Box>
      <Box
        sx={{
          width: 120,
          height: 120,
          mx: 'auto',
          mb: 3,
          position: 'relative',
        }}
      >
        <CircularProgress
          variant="determinate"
          value={100}
          size={120}
          thickness={4}
          sx={{ color: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] }}
        />
        <CircularProgress
          variant="determinate"
          value={progress}
          size={120}
          thickness={4}
          sx={{
            position: 'absolute',
            left: 0,
            color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
            '& .MuiCircularProgress-circle': { strokeLinecap: 'round' },
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography variant="h4" fontWeight={600} color="text.primary">
            {progress}%
          </Typography>
        </Box>
      </Box>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        {stage}
      </Typography>
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          maxWidth: 400,
          mx: 'auto',
          mt: 2,
          height: 8,
          borderRadius: 4,
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
          '& .MuiLinearProgress-bar': {
            borderRadius: 4,
            background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
          },
        }}
      />
      <Button
        variant="outlined"
        startIcon={<CancelIcon />}
        onClick={(e) => {
          e.stopPropagation()
          onCancel()
        }}
        sx={{ mt: 3, borderRadius: 1, textTransform: 'none' }}
      >
        Cancel
      </Button>
    </Box>
  )
}
