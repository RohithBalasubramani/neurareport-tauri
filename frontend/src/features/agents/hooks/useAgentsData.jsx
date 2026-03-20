/**
 * Agents Page - Custom hook for all state, effects, and callbacks
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import * as clientApi from '@/api/client'
import useAgentStore from '@/stores/agentStore'
import useSharedData from '@/hooks/useSharedData'
import useCrossPageActions from '@/hooks/useCrossPageActions'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { OutputType, FeatureKey } from '@/utils/crossPageTypes'
import { AGENTS } from '../components/AgentsStyledComponents'

export function useAgentsData() {
  const toast = useToast()
  const [searchParams, setSearchParams] = useSearchParams()
  const { execute } = useInteraction()
  const {
    tasks,
    executing,
    error,
    runResearch,
    runDataAnalysis,
    runEmailDraft,
    runContentRepurpose,
    runProofreading,
    runReportAnalyst,
    generateReportFromTask,
    fetchTasks,
    fetchAgentTypes,
    fetchRepurposeFormats,
    reset,
  } = useAgentStore()

  const { connections, templates, activeConnectionId } = useSharedData()
  const { registerOutput } = useCrossPageActions(FeatureKey.AGENTS)
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId)

  const [selectedAgent, setSelectedAgent] = useState(AGENTS[0])
  const [formData, setFormData] = useState({})
  const [showHistory, setShowHistory] = useState(false)
  const [result, setResult] = useState(null)
  const [recentRuns, setRecentRuns] = useState([])
  const [runsLoading, setRunsLoading] = useState(false)
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false)
  const resultRef = useRef(null)

  useEffect(() => {
    fetchAgentTypes()
    fetchRepurposeFormats()
    fetchTasks()
    return () => reset()
  }, [fetchAgentTypes, fetchRepurposeFormats, fetchTasks, reset])

  // Handle deep-link from Reports page: ?analyzeRunId=<run_id>
  useEffect(() => {
    const analyzeRunId = searchParams.get('analyzeRunId')
    if (analyzeRunId) {
      const reportAnalystAgent = AGENTS.find((a) => a.type === 'report_analyst')
      if (reportAnalystAgent) {
        setSelectedAgent(reportAnalystAgent)
        setFormData({ runId: analyzeRunId, analysisType: 'summarize' })
        const nextParams = new URLSearchParams(searchParams)
        nextParams.delete('analyzeRunId')
        setSearchParams(nextParams, { replace: true })
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch recent report runs when Report Analyst is selected
  useEffect(() => {
    if (selectedAgent?.type === 'report_analyst') {
      setRunsLoading(true)
      clientApi.listReportRuns({ limit: 20 })
        .then((runs) => setRecentRuns(Array.isArray(runs) ? runs : []))
        .catch(() => setRecentRuns([]))
        .finally(() => setRunsLoading(false))
    }
  }, [selectedAgent?.type])

  const handleSelectAgent = useCallback((agent) => {
    setSelectedAgent(agent)
    setFormData({})
    setResult(null)
  }, [])

  const handleFieldChange = useCallback((fieldName, value) => {
    setFormData((prev) => ({ ...prev, [fieldName]: value }))
  }, [])

  const handleRun = useCallback(async () => {
    if (!selectedAgent) return

    const runAction = async () => {
      let taskResult = null

      switch (selectedAgent.type) {
        case 'research':
          taskResult = await runResearch(formData.topic, {
            depth: formData.depth || 'comprehensive',
            maxSections: formData.maxSections || 5,
          })
          break
        case 'data_analyst':
          try {
            let data
            const dataSource = formData.dataSource || 'paste_spreadsheet'

            if (dataSource === 'sample_sales') {
              data = [
                { product: 'Widget A', revenue: 15000, units: 300, month: 'January' },
                { product: 'Widget B', revenue: 22000, units: 440, month: 'January' },
                { product: 'Widget A', revenue: 18000, units: 360, month: 'February' },
                { product: 'Widget B', revenue: 25000, units: 500, month: 'February' },
                { product: 'Widget C', revenue: 12000, units: 200, month: 'February' },
              ]
            } else if (dataSource === 'sample_inventory') {
              data = [
                { item: 'SKU-001', stock: 150, reorder_point: 50, supplier: 'Acme Corp' },
                { item: 'SKU-002', stock: 25, reorder_point: 30, supplier: 'Beta Inc' },
                { item: 'SKU-003', stock: 200, reorder_point: 75, supplier: 'Acme Corp' },
                { item: 'SKU-004', stock: 10, reorder_point: 20, supplier: 'Gamma Ltd' },
              ]
            } else if (dataSource === 'database_connection') {
              if (!selectedConnectionId) {
                toast.show('Please select a database connection', 'warning')
                return null
              }
              taskResult = await runDataAnalysis(formData.question, [], { connectionId: selectedConnectionId })
            } else if (dataSource === 'custom_json') {
              data = JSON.parse(formData.data)
            } else {
              const rawData = formData.data || ''
              const lines = rawData.trim().split('\n')
              if (lines.length < 2) {
                toast.show('Please paste data with at least a header row and one data row', 'warning')
                return null
              }
              const delimiter = lines[0].includes('\t') ? '\t' : ','
              const headers = lines[0].split(delimiter).map(h => h.trim().replace(/^["']|["']$/g, ''))
              data = lines.slice(1).map(line => {
                const values = line.split(delimiter).map(v => {
                  const trimmed = v.trim().replace(/^["']|["']$/g, '')
                  const num = parseFloat(trimmed)
                  return isNaN(num) ? trimmed : num
                })
                const row = {}
                headers.forEach((header, i) => {
                  row[header] = values[i] ?? ''
                })
                return row
              }).filter(row => Object.values(row).some(v => v !== ''))
            }

            if (dataSource !== 'database_connection') {
              if (!data || !data.length) {
                toast.show('No valid data found. Please check your input.', 'warning')
                return null
              }

              taskResult = await runDataAnalysis(formData.question, data)
            }
          } catch (parseError) {
            toast.show('Could not parse data. For custom JSON, ensure it\'s valid JSON format.', 'error')
            return null
          }
          break
        case 'email_draft':
          taskResult = await runEmailDraft(formData.context, formData.purpose, {
            tone: formData.tone || 'professional',
            recipientInfo: formData.recipientInfo,
          })
          break
        case 'content_repurpose':
          taskResult = await runContentRepurpose(
            formData.content,
            formData.sourceFormat || 'blog',
            formData.targetFormats || ['blog_summary'],
          )
          break
        case 'proofreading':
          taskResult = await runProofreading(formData.text, {
            styleGuide: formData.styleGuide !== 'None' ? formData.styleGuide : null,
          })
          break
        case 'report_analyst':
          taskResult = await runReportAnalyst(formData.runId, {
            analysisType: formData.analysisType || 'summarize',
            question: formData.question || null,
            compareRunId: formData.compareRunId || null,
          })
          break
        default:
          break
      }

      if (taskResult) {
        setResult(taskResult)
        if (taskResult.status === 'failed' || taskResult.status === 'error') {
          const errMsg = (typeof taskResult.error === 'object' ? taskResult.error?.message : taskResult.error) || taskResult.message || 'Agent task failed'
          toast.show(errMsg, 'error')
        } else {
          const taskOutput = taskResult.result || taskResult.output
          const outputText = (typeof taskOutput === 'string'
            ? taskOutput
            : JSON.stringify(taskOutput, null, 2)) || ''
          registerOutput({
            type: OutputType.TEXT,
            title: `${selectedAgent.name}: ${formData.topic || formData.question || formData.purpose || 'Result'}`,
            summary: outputText.substring(0, 200),
            data: outputText,
            format: 'text',
          })
          toast.show('Agent completed successfully', 'success')
        }
      }
      return taskResult
    }

    return execute({
      type: InteractionType.EXECUTE,
      label: `Run ${selectedAgent.name}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'agents', agentType: selectedAgent.type },
      action: runAction,
    })
  }, [execute, formData, runContentRepurpose, runDataAnalysis, runEmailDraft, runProofreading, runReportAnalyst, runResearch, selectedAgent, selectedConnectionId, toast])

  const handleCopyResult = useCallback(() => {
    const outputData = result?.result || result?.output
    if (outputData) {
      navigator.clipboard.writeText(typeof outputData === 'string' ? outputData : JSON.stringify(outputData, null, 2))
      toast.show('Copied to clipboard', 'success')
    }
  }, [result, toast])

  const handleToggleHistory = useCallback(() => {
    setShowHistory((prev) => !prev)
  }, [])

  const isFormValid = useCallback(() => {
    if (!selectedAgent) return false
    return selectedAgent.fields
      .filter((f) => f.required)
      .every((f) => formData[f.name]?.toString().trim())
  }, [selectedAgent, formData])

  const handleGenerateReport = useCallback(async (taskId, config) => {
    const res = await generateReportFromTask(taskId, config)
    if (res) {
      toast.show(`Report generation started! Job ID: ${res.job_id || 'queued'}`, 'success')
    }
  }, [generateReportFromTask, toast])

  return {
    tasks,
    executing,
    error,
    connections,
    templates,
    selectedConnectionId,
    selectedAgent,
    formData,
    showHistory,
    result,
    recentRuns,
    runsLoading,
    generateDialogOpen,
    resultRef,
    handleSelectAgent,
    handleFieldChange,
    handleRun,
    handleCopyResult,
    handleToggleHistory,
    isFormValid,
    setSelectedConnectionId,
    setResult,
    setSelectedAgent,
    setGenerateDialogOpen,
    handleGenerateReport,
  }
}
