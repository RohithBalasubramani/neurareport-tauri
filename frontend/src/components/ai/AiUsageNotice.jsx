import { Alert, Chip, Stack, Typography } from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'

export default function AiUsageNotice({
  title = 'AI output',
  description,
  chips = [],
  severity = 'info',
  dense = false,
  sx,
}) {
  return (
    <Alert
      icon={<AutoAwesomeIcon fontSize="small" />}
      severity={severity}
      sx={{
        borderRadius: 1,  // Figma spec: 8px
        alignItems: 'flex-start',
        '& .MuiAlert-message': { width: '100%' },
        ...sx,
      }}
    >
      <Stack spacing={dense ? 0.5 : 0.75}>
        {title && (
          <Typography variant={dense ? 'subtitle2' : 'subtitle1'} fontWeight={600}>
            {title}
          </Typography>
        )}
        {description && (
          <Typography variant="body2" color="text.secondary">
            {description}
          </Typography>
        )}
        {chips.length > 0 && (
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {chips.map((chip, idx) => (
              <Chip
                key={`${chip.label}-${idx}`}
                size="small"
                label={chip.label}
                color={chip.color}
                variant={chip.variant || (chip.color ? 'filled' : 'outlined')}
                sx={chip.sx}
              />
            ))}
          </Stack>
        )}
      </Stack>
    </Alert>
  )
}
