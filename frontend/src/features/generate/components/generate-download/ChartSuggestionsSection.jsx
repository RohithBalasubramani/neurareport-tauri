import {
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  Divider,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import BookmarkAddOutlinedIcon from '@mui/icons-material/BookmarkAddOutlined'

import { secondary } from '@/app/theme'
import SuggestedChartRenderer from './SuggestedChartRenderer.jsx'

export default function ChartSuggestionsSection({
  activeTemplate,
  chartQuestion,
  setChartQuestion,
  chartSuggestMutation,
  activeBatchData,
  handleAskCharts,
  chartSuggestions,
  selectedChartSource,
  selectedChartId,
  handleSelectSuggestion,
  selectedChartSpec,
  previewData,
  usingSampleData,
  handleSaveCurrentSuggestion,
  selectedSuggestion,
  saveChartLoading,
}) {
  if (!activeTemplate) return null

  return (
    <Box>
      <Divider sx={{ my: 2 }} />
      <Typography variant="subtitle1">AI chart suggestions</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
        Ask about the discovered batches for {activeTemplate.name || activeTemplate.id}.
      </Typography>
      <Stack spacing={1.5} sx={{ mt: 1.5 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.25}>
          <TextField
            fullWidth
            multiline
            minRows={2}
            maxRows={4}
            label="Ask a question about this template's data"
            placeholder="e.g. Highlight batches with unusually high row counts"
            value={chartQuestion}
            onChange={(event) => setChartQuestion(event.target.value)}
          />
          <Button
            variant="outlined"
            onClick={handleAskCharts}
            disabled={
              chartSuggestMutation.isLoading ||
              !activeBatchData.length
            }
            sx={{ alignSelf: { xs: 'flex-end', sm: 'flex-start' }, whiteSpace: 'nowrap' }}
          >
            {chartSuggestMutation.isLoading ? 'Asking for charts...' : 'Ask AI for charts'}
          </Button>
        </Stack>
        {!activeBatchData.length && (
          <Typography variant="caption" color="text.secondary">
            Run discovery for this template to unlock chart suggestions.
          </Typography>
        )}
        {chartSuggestions.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No suggestions yet. Ask a question to generate chart ideas.
          </Typography>
        ) : (
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Suggestions
              </Typography>
              <Stack spacing={1}>
                {chartSuggestions.map((chart) => (
                  <Card
                    key={chart.id}
                    variant={
                      selectedChartSource === 'suggestion' && chart.id === selectedChartId
                        ? 'outlined'
                        : 'elevation'
                    }
                    sx={{
                      borderColor:
                        selectedChartSource === 'suggestion' && chart.id === selectedChartId
                          ? 'text.secondary'
                          : 'divider',
                      bgcolor:
                        selectedChartSource === 'suggestion' && chart.id === selectedChartId
                          ? alpha(secondary.violet[500], 0.04)
                          : 'background.paper',
                    }}
                  >
                    <CardActionArea onClick={() => handleSelectSuggestion(chart.id)}>
                      <CardContent>
                        <Typography variant="subtitle2">
                          {chart.title || 'Untitled chart'}
                        </Typography>
                        {chart.description && (
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ mt: 0.5 }}
                          >
                            {chart.description}
                          </Typography>
                        )}
                        <Stack direction="row" spacing={1} sx={{ mt: 0.75, flexWrap: 'wrap' }}>
                          <Chip
                            size="small"
                            label={chart.type || 'chart'}
                            variant="outlined"
                            sx={{ textTransform: 'capitalize' }}
                          />
                          {chart.chartTemplateId && (
                            <Chip
                              size="small"
                              label={chart.chartTemplateId}
                              variant="outlined"
                            />
                          )}
                        </Stack>
                      </CardContent>
                    </CardActionArea>
                  </Card>
                ))}
              </Stack>
            </Box>
            <Box
              sx={{
                flex: 2,
                minHeight: { xs: 260, sm: 300 },
                borderRadius: 1.5,
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.paper',
                p: 1.5,
                minWidth: 0,
              }}
            >
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Preview
              </Typography>
              {usingSampleData && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  Using sample dataset from suggestion response
                </Typography>
              )}
              <Box sx={{ width: '100%', height: { xs: 220, sm: 260 } }}>
                <SuggestedChartRenderer
                  spec={selectedChartSpec}
                  data={previewData}
                  source={selectedChartSource}
                />
              </Box>
              {chartSuggestions.length > 0 && (
                <Box sx={{ textAlign: 'right', mt: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<BookmarkAddOutlinedIcon fontSize="small" />}
                    onClick={handleSaveCurrentSuggestion}
                    disabled={!selectedSuggestion || saveChartLoading}
                  >
                    {saveChartLoading ? 'Saving\u2026' : 'Save this chart'}
                  </Button>
                </Box>
              )}
            </Box>
          </Stack>
        )}
      </Stack>
    </Box>
  )
}
