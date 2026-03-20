/**
 * TopNav notifications dropdown menu
 */
import {
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Fade,
  alpha,
  useTheme,
} from '@mui/material'
import {
  Work as WorkIcon,
  Download as DownloadIcon,
  OpenInNew as OpenInNewIcon,
} from '@mui/icons-material'
import { StyledMenu, StyledMenuItem, MenuHeader, MenuLabel } from './TopNavStyles'

export default function TopNavNotificationsMenu({
  anchorEl,
  onClose,
  jobNotifications,
  downloadNotifications,
  onNavigate,
  onCloseNotifications,
  onOpenJobsPanel,
  onOpenDownload,
}) {
  const theme = useTheme()

  return (
    <StyledMenu
      anchorEl={anchorEl}
      open={Boolean(anchorEl)}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      TransitionComponent={Fade}
      slotProps={{ paper: { sx: { width: 320 } } }}
    >
      <MenuHeader>
        <MenuLabel>Jobs</MenuLabel>
      </MenuHeader>
      {jobNotifications.length ? jobNotifications.map((job) => (
        <StyledMenuItem
          key={job.id}
          onClick={() => {
            onCloseNotifications()
            onNavigate('/jobs', 'Open jobs')
          }}
        >
          <ListItemIcon>
            <WorkIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
          </ListItemIcon>
          <ListItemText
            primary={job.template_name || job.template_id || job.id}
            secondary={`Status: ${(job.status || 'unknown').toString()}`}
            primaryTypographyProps={{ fontSize: '14px' }}
            secondaryTypographyProps={{ fontSize: '0.75rem' }}
          />
        </StyledMenuItem>
      )) : (
        <MenuItem disabled sx={{ opacity: 0.5, mx: 1 }}>
          <ListItemText
            primary="No job updates yet"
            primaryTypographyProps={{ fontSize: '14px', color: 'text.secondary' }}
          />
        </MenuItem>
      )}

      <Divider sx={{ my: 1, mx: 1, borderColor: alpha(theme.palette.divider, 0.1) }} />

      <MenuHeader>
        <MenuLabel>Downloads</MenuLabel>
      </MenuHeader>
      {downloadNotifications.length ? downloadNotifications.map((download, index) => (
        <StyledMenuItem
          key={`${download.filename || download.template || 'download'}-${index}`}
          onClick={() => onOpenDownload(download)}
        >
          <ListItemIcon>
            <DownloadIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
          </ListItemIcon>
          <ListItemText
            primary={download.filename || download.template || 'Recent download'}
            secondary={download.format ? download.format.toUpperCase() : 'Open file'}
            primaryTypographyProps={{ fontSize: '14px' }}
            secondaryTypographyProps={{ fontSize: '0.75rem' }}
          />
        </StyledMenuItem>
      )) : (
        <MenuItem disabled sx={{ opacity: 0.5, mx: 1 }}>
          <ListItemText
            primary="No downloads yet"
            primaryTypographyProps={{ fontSize: '14px', color: 'text.secondary' }}
          />
        </MenuItem>
      )}

      <Divider sx={{ my: 1, mx: 1, borderColor: alpha(theme.palette.divider, 0.1) }} />

      <StyledMenuItem onClick={onOpenJobsPanel}>
        <ListItemIcon>
          <OpenInNewIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
        </ListItemIcon>
        <ListItemText
          primary="Open Jobs Panel"
          primaryTypographyProps={{ fontSize: '14px', fontWeight: 500 }}
        />
      </StyledMenuItem>
    </StyledMenu>
  )
}
