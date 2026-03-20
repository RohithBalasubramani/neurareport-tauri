/**
 * DrillDownBreadcrumb — breadcrumb navigation for DrillDownPanel.
 */
import {
  IconButton,
  Tooltip,
  Stack,
  Breadcrumbs,
  Link,
} from '@mui/material'
import {
  ChevronRight as ChevronIcon,
  ArrowBack as BackIcon,
  Home as HomeIcon,
} from '@mui/icons-material'
import { BreadcrumbContainer } from './DrillDownPanelStyles'

export default function DrillDownBreadcrumb({ currentPath, onDrillUp, onBreadcrumbClick }) {
  return (
    <BreadcrumbContainer>
      <Stack direction="row" alignItems="center" spacing={1}>
        {currentPath.length > 0 && (
          <Tooltip title="Go back">
            <IconButton size="small" onClick={() => onDrillUp?.()}>
              <BackIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
        <Breadcrumbs separator={<ChevronIcon sx={{ fontSize: 16 }} />} sx={{ fontSize: '14px' }}>
          <Link
            component="button"
            underline="hover"
            color={currentPath.length === 0 ? 'text.primary' : 'inherit'}
            onClick={() => onBreadcrumbClick(-1)}
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <HomeIcon sx={{ fontSize: 16 }} />
            All
          </Link>
          {currentPath.map((item, index) => (
            <Link
              key={item.id}
              component="button"
              underline="hover"
              color={index === currentPath.length - 1 ? 'text.primary' : 'inherit'}
              onClick={() => onBreadcrumbClick(index)}
              sx={{ fontWeight: index === currentPath.length - 1 ? 600 : 400 }}
            >
              {item.label}
            </Link>
          ))}
        </Breadcrumbs>
      </Stack>
    </BreadcrumbContainer>
  )
}
