/**
 * Sidebar for visualization page: diagram type picker + data input.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  CircularProgress,
  alpha,
  useTheme,
} from '@mui/material'
import {
  AccountTree as FlowchartIcon,
  Hub as MindmapIcon,
  Groups as OrgChartIcon,
  Timeline as TimelineIcon,
  ViewKanban as KanbanIcon,
  BubbleChart as NetworkIcon,
  FormatListNumbered as GanttIcon,
  SwapVert as SequenceIcon,
  Cloud as WordcloudIcon,
  Visibility as PreviewIcon,
  UploadFile as UploadFileIcon,
} from '@mui/icons-material'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { DIAGRAM_TYPES } from '../hooks/useVisualizationPage'

const ICON_MAP = {
  flowchart: FlowchartIcon,
  mindmap: MindmapIcon,
  org_chart: OrgChartIcon,
  timeline: TimelineIcon,
  gantt: GanttIcon,
  kanban: KanbanIcon,
  network: NetworkIcon,
  sequence: SequenceIcon,
  wordcloud: WordcloudIcon,
}

export default function VisualizationSidebar({
  selectedType,
  handleTypeChange,
  title,
  setTitle,
  selectedConnectionId,
  setSelectedConnectionId,
  fileInputRef,
  handleFileUpload,
  uploadingFile,
  uploadedFileName,
  inputData,
  setInputData,
  generating,
  handleGenerate,
  Sidebar,
  DiagramTypeCard,
  ActionButton,
}) {
  const theme = useTheme()

  return (
    <Sidebar>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
        Diagram Type
      </Typography>
      {DIAGRAM_TYPES.map((type) => {
        const Icon = ICON_MAP[type.type]
        return (
          <DiagramTypeCard
            key={type.type}
            selected={selectedType.type === type.type}
            onClick={() => handleTypeChange(type)}
          >
            <Box sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    borderRadius: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: alpha(theme.palette.text.primary, 0.08),
                  }}
                >
                  {Icon && <Icon sx={{ color: 'text.secondary', fontSize: 18 }} />}
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {type.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {type.description}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </DiagramTypeCard>
        )
      })}

      {/* Input Section */}
      <Box sx={{ mt: 3 }}>
        <TextField
          fullWidth
          size="small"
          label="Title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          sx={{ mb: 2 }}
        />
        <ConnectionSelector
          value={selectedConnectionId}
          onChange={setSelectedConnectionId}
          label="Data Source"
          size="small"
          showStatus
          sx={{ mb: 2 }}
        />
        {/* File Upload */}
        <input
          ref={fileInputRef}
          type="file"
          hidden
          accept=".xlsx,.xls,.csv"
          onChange={handleFileUpload}
        />
        <Button
          fullWidth
          variant="outlined"
          size="small"
          startIcon={uploadingFile ? <CircularProgress size={16} color="inherit" /> : <UploadFileIcon />}
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadingFile}
          sx={{ mb: 1, textTransform: 'none', borderStyle: 'dashed' }}
        >
          {uploadingFile ? 'Extracting data...' : 'Upload Excel / CSV'}
        </Button>
        {uploadedFileName && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, textAlign: 'center' }}>
            {uploadedFileName}
          </Typography>
        )}
        <TextField
          fullWidth
          multiline
          rows={8}
          label="Data Input"
          placeholder="Upload an Excel/CSV file or paste data here..."
          value={inputData}
          onChange={(e) => setInputData(e.target.value)}
          sx={{ mb: 2 }}
        />
        <ActionButton
          variant="contained"
          fullWidth
          startIcon={generating ? <CircularProgress size={20} color="inherit" /> : <PreviewIcon />}
          onClick={handleGenerate}
          disabled={!inputData.trim() || generating}
        >
          {generating ? 'Generating...' : 'Generate'}
        </ActionButton>
      </Box>
    </Sidebar>
  )
}
