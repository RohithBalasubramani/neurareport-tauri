/**
 * Sidebar navigation section with items
 */
import {
  Box,
  Typography,
  Tooltip,
  Badge,
  Collapse,
  alpha,
  useTheme,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { neutral, fontFamilyUI } from '@/app/theme'
import { slideIn } from './SidebarStyles'
import { SectionHeader, NavItemButton, NavIcon } from './SidebarNavStyles'

export default function SidebarSection({
  section,
  collapsed,
  isExpanded,
  isLast,
  activeJobs,
  isActive,
  handleNavigate,
  handleToggleSection,
}) {
  const theme = useTheme()

  return (
    <Box>
      {/* Section Header */}
      {!collapsed && (
        <SectionHeader
          collapsed={collapsed}
          collapsible={section.collapsible}
          onClick={() => section.collapsible && handleToggleSection(section.section)}
        >
          <Typography
            sx={{
              // FIGMA: Small Text style - Inter Medium
              fontFamily: fontFamilyUI,
              fontSize: '10px',
              fontWeight: 600,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
            }}
          >
            {section.section}
          </Typography>
          {section.collapsible && (
            <ExpandMoreIcon
              className="expand-icon"
              sx={{
                fontSize: 16,
                color: 'text.disabled',
                transition: 'transform 0.2s ease',
                transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
              }}
            />
          )}
        </SectionHeader>
      )}

      {/* Section Items */}
      <Collapse in={collapsed || isExpanded}>
        <Box sx={{ py: 0.5 }}>
          {section.items.map((item, itemIndex) => {
            const Icon = item.icon
            const active = isActive(item.path)
            const badgeContent = item.badge ? activeJobs : 0

            return (
              <Tooltip
                key={item.key}
                title={collapsed ? item.label : ''}
                placement="right"
                arrow
              >
                <NavItemButton
                  active={active}
                  collapsed={collapsed}
                  highlight={item.highlight}
                  component="button"
                  type="button"
                  aria-current={active ? 'page' : undefined}
                  onClick={() => handleNavigate(item.path)}
                  sx={{
                    animation: `${slideIn} 0.2s ease-out ${itemIndex * 30}ms both`,
                  }}
                >
                  <NavIcon active={active} highlight={item.highlight}>
                    <Badge
                      badgeContent={badgeContent}
                      invisible={!badgeContent}
                      sx={{
                        '& .MuiBadge-badge': {
                          bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
                          color: 'text.secondary',
                          fontSize: '10px',
                          fontWeight: 600,
                          minWidth: 14,
                          height: 14,
                          padding: '0 3px',
                        },
                      }}
                    >
                      <Icon />
                    </Badge>
                  </NavIcon>

                  {!collapsed && (
                    <Typography
                      sx={{
                        // FIGMA: Navigation Item - Inter Medium 16px
                        fontFamily: fontFamilyUI,
                        fontSize: '16px',
                        fontWeight: 500,
                        lineHeight: 'normal',
                        flex: 1,
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {item.label}
                    </Typography>
                  )}

                  {/* Removed sparkle icons - not in Figma design */}
                </NavItemButton>
              </Tooltip>
            )
          })}
        </Box>
      </Collapse>

      {/* Section Divider */}
      {!isLast && (
        <Box
          sx={{
            height: 1,
            mx: 2,
            my: 1.5,
            bgcolor: alpha(theme.palette.divider, 0.3),
          }}
        />
      )}
    </Box>
  )
}
