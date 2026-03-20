import { Box, Typography, Stack, Button } from '@mui/material'
import LoadingState from '@/components/feedback/LoadingState.jsx'

export default function VerifyProgressPanel({
  verifying,
  verifyLog,
  verifyStageLabel,
  verifyProgress,
  verifyEtaText,
  onViewDetails,
}) {
  if (!verifying && !verifyLog.length) return null
  return (
    <Box
      sx={{
        mt: 2,
        p: 2,
        borderRadius: 1,
        border: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      <Stack spacing={1.25}>
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Typography variant="subtitle2">Verification progress</Typography>
          <Button
            size="small"
            variant="text"
            onClick={onViewDetails}
            sx={{ textTransform: 'none' }}
          >
            View details
          </Button>
        </Stack>
        <LoadingState
          label={verifyStageLabel}
          progress={verifyProgress}
          description={verifyEtaText}
        />
        {!!verifyLog.length && (
          <Stack spacing={0.5}>
            {verifyLog.slice(-3).map((entry) => (
              <Typography
                key={`inline-${entry.key}`}
                variant="caption"
                color="text.secondary"
              >
                {entry.label || entry.key}
              </Typography>
            ))}
          </Stack>
        )}
      </Stack>
    </Box>
  )
}
