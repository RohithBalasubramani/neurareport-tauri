/**
 * Job Details Dialog Component
 */
import { Box, Stack, Tooltip, useTheme } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import DownloadIcon from '@mui/icons-material/Download'
import ReplayIcon from '@mui/icons-material/Replay'
import { canRetryJob, JobStatus } from '@/utils/jobStatus'
import { MonoText, StatusChip, ActionButton } from './JobsStyledComponents'
import {
  StyledDialog,
  DialogHeader,
  CloseButton,
  StyledDialogContent,
  StyledDialogActions,
  DetailLabel,
  DetailValue,
  ResultBox,
  StyledDivider,
  ErrorAlert,
  getStatusConfig,
} from './JobsDialogStyles'

export default function JobDetailsDialog({
  open,
  detailsJob,
  retrying,
  onClose,
  onDownload,
  onRetry,
}) {
  const theme = useTheme()

  return (
    <StyledDialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogHeader>
        Job Details
        <Tooltip title="Close">
          <CloseButton size="small" onClick={onClose} aria-label="Close dialog">
            <CloseIcon sx={{ fontSize: 18 }} />
          </CloseButton>
        </Tooltip>
      </DialogHeader>
      <StyledDialogContent>
        {detailsJob && (
          <Stack spacing={2} sx={{ pt: 2 }}>
            <Box>
              <DetailLabel>Job ID</DetailLabel>
              <MonoText sx={{ fontSize: '14px' }}>
                {detailsJob.id}
              </MonoText>
            </Box>
            <StyledDivider />
            <Box>
              <DetailLabel>Status</DetailLabel>
              <Box sx={{ mt: 0.5 }}>
                {(() => {
                  const config = getStatusConfig(theme, detailsJob.status)
                  const Icon = config.icon
                  return (
                    <StatusChip
                      icon={<Icon sx={{ fontSize: 14 }} />}
                      label={config.label}
                      size="small"
                      statusColor={config.color}
                      statusBg={config.bgColor}
                    />
                  )
                })()}
              </Box>
            </Box>
            <StyledDivider />
            <Box>
              <DetailLabel>Template</DetailLabel>
              <DetailValue>
                {detailsJob.templateName || detailsJob.templateId || detailsJob.template_id || '-'}
              </DetailValue>
            </Box>
            {(detailsJob.connectionId || detailsJob.connection_id) && (
              <>
                <StyledDivider />
                <Box>
                  <DetailLabel>Connection ID</DetailLabel>
                  <MonoText>
                    {detailsJob.connectionId || detailsJob.connection_id}
                  </MonoText>
                </Box>
              </>
            )}
            <StyledDivider />
            <Box>
              <DetailLabel>Created</DetailLabel>
              <DetailValue>
                {detailsJob.createdAt ? new Date(detailsJob.createdAt).toLocaleString() : '-'}
              </DetailValue>
            </Box>
            {(detailsJob.finishedAt || detailsJob.completed_at) && (
              <>
                <StyledDivider />
                <Box>
                  <DetailLabel>Completed</DetailLabel>
                  <DetailValue>
                    {new Date(detailsJob.finishedAt || detailsJob.completed_at).toLocaleString()}
                  </DetailValue>
                </Box>
              </>
            )}
            {detailsJob.error && (
              <>
                <StyledDivider />
                <ErrorAlert severity="error">
                  {detailsJob.error}
                </ErrorAlert>
              </>
            )}
            {(() => {
              const resultPayload = detailsJob?.result && Object.keys(detailsJob.result || {}).length
                ? detailsJob.result
                : null
              if (!resultPayload) return null
              const summaryText = typeof resultPayload.summary === 'string' ? resultPayload.summary : null
              const bodyText = summaryText || JSON.stringify(resultPayload, null, 2)
              return (
                <>
                  <StyledDivider />
                  <Box>
                    <DetailLabel>Result</DetailLabel>
                    <ResultBox component="pre">
                      {bodyText}
                    </ResultBox>
                  </Box>
                </>
              )
            })()}
          </Stack>
        )}
      </StyledDialogContent>
      <StyledDialogActions>
        {detailsJob?.status === JobStatus.COMPLETED && detailsJob?.artifacts?.html_url && (
          <ActionButton
            variant="outlined"
            size="small"
            startIcon={<DownloadIcon sx={{ fontSize: 16 }} />}
            onClick={onDownload}
          >
            Download
          </ActionButton>
        )}
        {canRetryJob(detailsJob?.status) && (
          <ActionButton
            variant="outlined"
            size="small"
            startIcon={<ReplayIcon sx={{ fontSize: 16 }} />}
            disabled={retrying}
            onClick={onRetry}
          >
            {retrying ? 'Retrying...' : 'Retry'}
          </ActionButton>
        )}
        <ActionButton onClick={onClose}>
          Close
        </ActionButton>
      </StyledDialogActions>
    </StyledDialog>
  )
}
