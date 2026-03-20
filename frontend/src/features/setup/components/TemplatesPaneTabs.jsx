import {
  Box, Tabs, Tab, Badge,
} from '@mui/material'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import TuneIcon from '@mui/icons-material/Tune'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { neutral } from '@/app/theme'
import Surface from '@/components/layout/Surface.jsx'
import TemplatePicker from '@/features/generate/components/TemplatePicker.jsx'

export function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`run-tabpanel-${index}`}
      aria-labelledby={`run-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  )
}

export default function TemplatesPaneTabs({
  activeTab,
  handleTabChange,
  selectedCount,
  schedulesCount,
  selected,
  onToggle,
  outputFormats,
  setOutputFormats,
  tagFilter,
  setTagFilter,
  handleNavigate,
  configureContent,
  schedulesContent,
}) {
  return (
    <Surface sx={{ p: 0 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            px: 2,
            '& .MuiTab-root': {
              minHeight: 48,
              textTransform: 'none',
              fontWeight: 600,
            },
          }}
        >
          <Tab
            icon={<Badge badgeContent={selectedCount} sx={{ '& .MuiBadge-badge': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white' } }}><CheckRoundedIcon /></Badge>}
            iconPosition="start"
            label="Designs"
          />
          <Tab
            icon={<TuneIcon />}
            iconPosition="start"
            label="Configure"
          />
          <Tab
            icon={<Badge badgeContent={schedulesCount || undefined} sx={{ '& .MuiBadge-badge': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700], color: 'common.white' } }}><ScheduleIcon /></Badge>}
            iconPosition="start"
            label="Schedules"
          />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        <Box sx={{ px: 2, pb: 2 }}>
          <TemplatePicker
            selected={selected}
            onToggle={onToggle}
            outputFormats={outputFormats}
            setOutputFormats={setOutputFormats}
            tagFilter={tagFilter}
            setTagFilter={setTagFilter}
            onEditTemplate={(tpl) => {
              if (!tpl?.id) return
              handleNavigate(`/templates/${tpl.id}/edit`, 'Edit template', {
                templateId: tpl.id,
                from: '/',
              })
            }}
          />
        </Box>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        {configureContent}
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        {schedulesContent}
      </TabPanel>
    </Surface>
  )
}
