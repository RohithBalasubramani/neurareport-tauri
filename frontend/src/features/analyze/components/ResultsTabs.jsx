import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Fade,
  alpha,
  useTheme,
} from '@mui/material'
import InsightsOutlinedIcon from '@mui/icons-material/InsightsOutlined'
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer'
import BarChartIcon from '@mui/icons-material/BarChart'
import TableChartIcon from '@mui/icons-material/TableChart'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'
import TabPanel from './TabPanel'
import OverviewTab from './OverviewTab'
import QATab from './QATab'
import ChartsTab from './ChartsTab'
import DataTab from './DataTab'
import InsightsTab from './InsightsTab'

export default function ResultsTabs({
  activeTab,
  onTabChange,
  analysisResult,
  // QA props
  question,
  setQuestion,
  isAskingQuestion,
  qaHistory,
  suggestedQuestions,
  onAskQuestion,
  // Chart props
  chartQuery,
  setChartQuery,
  isGeneratingCharts,
  generatedCharts,
  onGenerateCharts,
}) {
  const theme = useTheme()

  return (
    <Fade in>
      <Box>
        {/* Warnings from partial failures */}
        {analysisResult.warnings?.length > 0 && (
          <Paper
            sx={{
              mb: 2,
              p: 2,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.warning.main, 0.1) : alpha(theme.palette.warning.main, 0.05),
              border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
              borderRadius: 1,
            }}
          >
            <Typography variant="body2" color="warning.main" sx={{ fontWeight: 500 }}>
              Analysis completed with warnings:
            </Typography>
            {analysisResult.warnings.map((w, i) => (
              <Typography key={i} variant="body2" color="text.secondary" sx={{ ml: 2, mt: 0.5 }}>
                {w}
              </Typography>
            ))}
          </Paper>
        )}

        {/* Tabs */}
        <GlassCard hover={false} sx={{ p: 0, mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={(e, v) => onTabChange(v)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '16px',
                minHeight: 64,
                transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
                '&:hover': {
                  bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                },
                '&.Mui-selected': {
                  color: 'text.primary',
                },
              },
              '& .MuiTabs-indicator': {
                height: 3,
                borderRadius: '3px 3px 0 0',
                background: theme.palette.mode === 'dark' ? neutral[500] : neutral[900],
              },
            }}
          >
            <Tab icon={<InsightsOutlinedIcon />} iconPosition="start" label="Overview" />
            <Tab icon={<QuestionAnswerIcon />} iconPosition="start" label="Q&A" />
            <Tab icon={<BarChartIcon />} iconPosition="start" label="Charts" />
            <Tab icon={<TableChartIcon />} iconPosition="start" label="Data" />
            <Tab icon={<LightbulbIcon />} iconPosition="start" label="Insights" />
          </Tabs>
        </GlassCard>

        <TabPanel value={activeTab} index={0}>
          <OverviewTab analysisResult={analysisResult} />
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <QATab
            question={question}
            setQuestion={setQuestion}
            isAskingQuestion={isAskingQuestion}
            qaHistory={qaHistory}
            suggestedQuestions={suggestedQuestions}
            onAskQuestion={onAskQuestion}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <ChartsTab
            chartQuery={chartQuery}
            setChartQuery={setChartQuery}
            isGeneratingCharts={isGeneratingCharts}
            generatedCharts={generatedCharts}
            onGenerateCharts={onGenerateCharts}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <DataTab analysisResult={analysisResult} />
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
          <InsightsTab analysisResult={analysisResult} />
        </TabPanel>
      </Box>
    </Fade>
  )
}
