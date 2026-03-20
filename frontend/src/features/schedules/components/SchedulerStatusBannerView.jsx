/**
 * Scheduler status banner component.
 */
import { Typography } from '@mui/material'
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material'
import { SchedulerStatusBanner } from './ScheduleStyles'

export default function SchedulerStatusBannerView({ schedulerStatus }) {
  if (!schedulerStatus) return null

  const { scheduler, schedules: schedInfo } = schedulerStatus
  const isRunning = scheduler?.running
  const isEnabled = scheduler?.enabled

  let statusIcon = <InfoIcon />
  let statusText = ''
  let bannerStatus = 'warning'

  if (!isEnabled) {
    statusIcon = <WarningIcon />
    statusText = 'Scheduler is disabled. Schedules will not run automatically.'
    bannerStatus = 'disabled'
  } else if (!isRunning) {
    statusIcon = <WarningIcon />
    statusText = 'Scheduler is not running. Restart the server to enable automatic scheduling.'
    bannerStatus = 'warning'
  } else {
    statusIcon = <CheckCircleIcon />
    bannerStatus = 'ok'
    if (schedInfo?.next_run) {
      const nextRunTime = new Date(schedInfo.next_run.next_run_at).toLocaleString()
      statusText = `Scheduler running. Next: "${schedInfo.next_run.schedule_name}" at ${nextRunTime}`
    } else {
      statusText = `Scheduler running (polling every ${scheduler?.poll_interval_seconds || 60}s). ${schedInfo?.active || 0} active schedule(s).`
    }
  }

  return (
    <SchedulerStatusBanner status={bannerStatus}>
      {statusIcon}
      <Typography variant="body2" fontWeight={500}>
        {statusText}
      </Typography>
    </SchedulerStatusBanner>
  )
}
