import { useCallback, useState, useMemo } from 'react'
import {
  Box,
  Typography,
  alpha,
  useTheme,
} from '@mui/material'
import { neutral } from '@/app/theme'

import useFileAnalysis from '../hooks/useFileAnalysis'
import useAnalysisQA from '../hooks/useAnalysisQA'
import useChartGeneration from '../hooks/useChartGeneration'
import useAnalysisExport from '../hooks/useAnalysisExport'

import AnalyzeHeader from '../components/AnalyzeHeader'
import UploadSection from '../components/UploadSection'
import ResultsTabs from '../components/ResultsTabs'

export default function EnhancedAnalyzePageContainer() {
  const theme = useTheme()
  const [activeTab, setActiveTab] = useState(0)
  const [selectedConnectionId, setSelectedConnectionId] = useState('')
  const [selectedTemplateId, setSelectedTemplateId] = useState('')

  // analysisId is extracted after fileAnalysis populates its result,
  // but we need to declare hooks unconditionally. We use a separate
  // piece of state so the QA/Chart/Export hooks always see the latest id.
  const [analysisId, setAnalysisId] = useState(null)

  const qa = useAnalysisQA({ analysisId })
  const charts = useChartGeneration({ analysisId })
  const exportHook = useAnalysisExport({ analysisId })

  const handleAnalysisComplete = useCallback((result, initialCharts) => {
    setAnalysisId(result.analysis_id)
    qa.initSuggestedQuestions(result.suggested_questions)
    charts.initCharts(initialCharts)
    setActiveTab(0)
  }, [qa, charts])

  const fileAnalysis = useFileAnalysis({
    selectedConnectionId,
    selectedTemplateId,
    onAnalysisComplete: handleAnalysisComplete,
  })

  const stats = useMemo(() => {
    if (!fileAnalysis.analysisResult) return null
    const r = fileAnalysis.analysisResult
    return {
      tables: r.total_tables || r.tables?.length || 0,
      metrics: r.total_metrics || r.metrics?.length || 0,
      entities: r.total_entities || r.entities?.length || 0,
      insights: r.insights?.length || 0,
      risks: r.risks?.length || 0,
      opportunities: r.opportunities?.length || 0,
      charts: charts.generatedCharts.length,
    }
  }, [fileAnalysis.analysisResult, charts.generatedCharts.length])

  const handleReset = useCallback(() => {
    fileAnalysis.handleReset()
    qa.resetQA()
    charts.resetCharts()
    setAnalysisId(null)
    setActiveTab(0)
  }, [fileAnalysis, qa, charts])

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: theme.palette.mode === 'dark'
          ? `linear-gradient(180deg, ${alpha(theme.palette.text.primary, 0.02)} 0%, ${theme.palette.background.default} 50%)`
          : `linear-gradient(180deg, ${neutral[50]} 0%, ${theme.palette.background.default} 50%)`,
      }}
    >
      <AnalyzeHeader
        stats={stats}
        analysisResult={fileAnalysis.analysisResult}
        isExporting={exportHook.isExporting}
        exportMenuAnchor={exportHook.exportMenuAnchor}
        onExportClick={(e) => exportHook.setExportMenuAnchor(e.currentTarget)}
        onExportClose={() => exportHook.setExportMenuAnchor(null)}
        onExport={exportHook.handleExport}
        onReset={handleReset}
      />

      <Box sx={{ px: 4, py: 3, maxWidth: 1400, mx: 'auto', width: '100%' }}>
        {!fileAnalysis.analysisResult && (
          <UploadSection
            selectedFile={fileAnalysis.selectedFile}
            isDragOver={fileAnalysis.isDragOver}
            isAnalyzing={fileAnalysis.isAnalyzing}
            analysisProgress={fileAnalysis.analysisProgress}
            progressStage={fileAnalysis.progressStage}
            error={fileAnalysis.error}
            fileInputRef={fileAnalysis.fileInputRef}
            selectedConnectionId={selectedConnectionId}
            selectedTemplateId={selectedTemplateId}
            onConnectionChange={setSelectedConnectionId}
            onTemplateChange={setSelectedTemplateId}
            onDragOver={fileAnalysis.handleDragOver}
            onDragLeave={fileAnalysis.handleDragLeave}
            onDrop={fileAnalysis.handleDrop}
            onFileSelect={fileAnalysis.handleFileSelect}
            onAnalyze={fileAnalysis.handleAnalyze}
            onCancelAnalysis={fileAnalysis.handleCancelAnalysis}
          />
        )}

        {fileAnalysis.analysisResult && (
          <ResultsTabs
            activeTab={activeTab}
            onTabChange={setActiveTab}
            analysisResult={fileAnalysis.analysisResult}
            question={qa.question}
            setQuestion={qa.setQuestion}
            isAskingQuestion={qa.isAskingQuestion}
            qaHistory={qa.qaHistory}
            suggestedQuestions={qa.suggestedQuestions}
            onAskQuestion={qa.handleAskQuestion}
            chartQuery={charts.chartQuery}
            setChartQuery={charts.setChartQuery}
            isGeneratingCharts={charts.isGeneratingCharts}
            generatedCharts={charts.generatedCharts}
            onGenerateCharts={charts.handleGenerateCharts}
          />
        )}

        {/* Footer */}
        <Box sx={{ textAlign: 'center', py: 4, mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Supported formats: PDF, Excel (XLSX, XLS), CSV, Word, Images
          </Typography>
          <Typography variant="caption" color="text.disabled" sx={{ mt: 0.5, display: 'block' }}>
            AI-powered analysis with intelligent extraction, multi-mode summaries, Q&A, and visualization
          </Typography>
        </Box>
      </Box>
    </Box>
  )
}
