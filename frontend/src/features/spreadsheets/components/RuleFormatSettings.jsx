/**
 * Rule Format Settings
 * Color and font style settings for conditional formatting rules.
 */
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Stack,
  Chip,
  alpha,
  useTheme,
  styled,
} from '@mui/material'
import {
  FormatColorFill as FillIcon,
  FormatColorText as TextColorIcon,
  FormatBold as BoldIcon,
  FormatItalic as ItalicIcon,
} from '@mui/icons-material'
import { PRESET_STYLES } from '../hooks/useConditionalFormat'

const ColorPreview = styled(Box)(({ theme, bgcolor, textcolor }) => ({
  width: 60,
  height: 28,
  borderRadius: 4,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: bgcolor || theme.palette.background.default,
  color: textcolor || theme.palette.text.primary,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  fontSize: '0.75rem',
  fontWeight: 600,
}))

const ColorInput = styled('input')(({ theme }) => ({
  width: 40,
  height: 32,
  padding: 0,
  border: 'none',
  borderRadius: 4,
  cursor: 'pointer',
  backgroundColor: 'transparent',
  '&::-webkit-color-swatch-wrapper': {
    padding: 0,
  },
  '&::-webkit-color-swatch': {
    border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
    borderRadius: 4,
  },
}))

export default function RuleFormatSettings({ format, onFormatChange }) {
  const theme = useTheme()

  return (
    <>
      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
        Format
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        {PRESET_STYLES.map((preset, i) => (
          <Chip
            key={i}
            label={preset.label}
            size="small"
            onClick={() => {
              onFormatChange('fill', preset.fill)
              onFormatChange('text', preset.text)
            }}
            sx={{
              backgroundColor: preset.fill,
              color: preset.text,
              '&:hover': { backgroundColor: preset.fill },
            }}
          />
        ))}
      </Stack>
      <Stack direction="row" spacing={2} alignItems="center">
        <Stack direction="row" spacing={1} alignItems="center">
          <FillIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="caption">Fill:</Typography>
          <ColorInput
            type="color"
            value={format.fill || '#ffffff'}
            onChange={(e) => onFormatChange('fill', e.target.value)}
          />
        </Stack>
        <Stack direction="row" spacing={1} alignItems="center">
          <TextColorIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="caption">Text:</Typography>
          <ColorInput
            type="color"
            value={format.text || '#000000'}
            onChange={(e) => onFormatChange('text', e.target.value)}
          />
        </Stack>
      </Stack>
      <Stack direction="row" spacing={1}>
        <Tooltip title="Bold">
          <IconButton
            size="small"
            onClick={() => onFormatChange('bold', !format.bold)}
            sx={{ border: `1px solid ${alpha(theme.palette.divider, 0.2)}`, color: format.bold ? 'text.primary' : 'text.secondary' }}
          >
            <BoldIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Italic">
          <IconButton
            size="small"
            onClick={() => onFormatChange('italic', !format.italic)}
            sx={{ border: `1px solid ${alpha(theme.palette.divider, 0.2)}`, color: format.italic ? 'text.primary' : 'text.secondary' }}
          >
            <ItalicIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>
      <Box>
        <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
          Preview:
        </Typography>
        <ColorPreview
          bgcolor={format.fill}
          textcolor={format.text}
          sx={{
            width: '100%',
            height: 40,
            fontWeight: format.bold ? 600 : 400,
            fontStyle: format.italic ? 'italic' : 'normal',
          }}
        >
          Sample Cell
        </ColorPreview>
      </Box>
    </>
  )
}
