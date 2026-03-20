/**
 * Custom hook for visualization page state and actions.
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import useVisualizationStore from '@/stores/visualizationStore'
import useSharedData from '@/hooks/useSharedData'
import useCrossPageActions from '@/hooks/useCrossPageActions'
import { OutputType, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { extractExcel } from '@/api/visualization'

const DIAGRAM_TYPES = [
  { type: 'flowchart', name: 'Flowchart', description: 'Process and decision flows' },
  { type: 'mindmap', name: 'Mind Map', description: 'Hierarchical idea mapping' },
  { type: 'org_chart', name: 'Org Chart', description: 'Organizational structure' },
  { type: 'timeline', name: 'Timeline', description: 'Chronological events' },
  { type: 'gantt', name: 'Gantt Chart', description: 'Project scheduling' },
  { type: 'kanban', name: 'Kanban Board', description: 'Task management' },
  { type: 'network', name: 'Network Graph', description: 'Connections and relationships' },
  { type: 'sequence', name: 'Sequence Diagram', description: 'Process interactions' },
  { type: 'wordcloud', name: 'Word Cloud', description: 'Text frequency visualization' },
]

export { DIAGRAM_TYPES }

export function useVisualizationPage() {
  const toast = useToast()
  const { execute } = useInteraction()
  const {
    diagrams,
    currentDiagram,
    loading,
    generating,
    error,
    generateFlowchart,
    generateMindmap,
    generateOrgChart,
    generateTimeline,
    generateGantt,
    generateKanban,
    generateNetworkGraph,
    generateSequenceDiagram,
    generateWordcloud,
    exportAsMermaid,
    exportAsSvg,
    exportAsPng,
    setCurrentDiagram,
    reset,
  } = useVisualizationStore()

  const { connections, activeConnectionId } = useSharedData()
  const { registerOutput } = useCrossPageActions(FeatureKey.VISUALIZATION)
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId || '')

  const [selectedType, setSelectedType] = useState(DIAGRAM_TYPES[0])
  const [inputData, setInputData] = useState('')
  const [title, setTitle] = useState('')
  const [options, setOptions] = useState({})
  const [uploadingFile, setUploadingFile] = useState(false)
  const [uploadedFileName, setUploadedFileName] = useState('')
  const [extractedTable, setExtractedTable] = useState(null)
  const [previewType, setPreviewType] = useState(null)
  const fileInputRef = useRef(null)
  const activeDiagram = currentDiagram && previewType === selectedType.type ? currentDiagram : null

  useEffect(() => {
    return () => reset()
  }, [reset])

  const handleTypeChange = useCallback((type) => {
    setSelectedType(type)
    setInputData('')
    setTitle('')
    setUploadedFileName('')
    setExtractedTable(null)
    setPreviewType(null)
    setCurrentDiagram(null)
  }, [setCurrentDiagram])

  const handleFileUpload = useCallback(async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    e.target.value = ''

    setPreviewType(null)
    setCurrentDiagram(null)
    setUploadingFile(true)
    setUploadedFileName(file.name)
    try {
      const result = await extractExcel(file)
      let headers = []
      let rows = []

      if (result?.sheets?.length > 0) {
        const sheet = result.sheets[0]
        headers = sheet.headers || []
        rows = (sheet.rows || []).slice(0, 200)
      }

      if (headers.length > 0 && rows.length > 0) {
        const jsonRows = rows.map((row) => {
          const obj = {}
          headers.forEach((h, i) => { obj[h] = row[i] })
          return obj
        })
        setExtractedTable({ headers, rows, filename: file.name, sheetCount: result.total_sheets || 1 })
        setInputData(JSON.stringify(jsonRows, null, 2))
        setTitle(file.name.replace(/\.[^.]+$/, ''))
        toast.show(`Extracted ${rows.length} rows, ${headers.length} columns from ${file.name}`, 'success')
      } else {
        toast.show('No data found in file', 'warning')
      }
    } catch (err) {
      toast.show(err.message || 'Failed to extract data from file', 'error')
    } finally {
      setUploadingFile(false)
    }
  }, [setCurrentDiagram, toast])

  const handleGenerate = useCallback(async () => {
    if (!inputData.trim()) {
      toast.show('Please enter data', 'warning')
      return
    }

    const generateAction = async () => {
      let result = null
      const opts = { title, ...options }

      let parsedRows = null
      try {
        const parsed = JSON.parse(inputData)
        if (Array.isArray(parsed)) parsedRows = parsed
      } catch { /* not JSON, use as plain text */ }

      const colValues = (rows) => {
        const keys = Object.keys(rows[0] || {})
        return keys.length === 1
          ? rows.map((r) => Object.values(r)[0]).filter(Boolean)
          : rows.map((r) => Object.values(r).join(' - ')).filter(Boolean)
      }

      try {
        switch (selectedType.type) {
          case 'flowchart': {
            const steps = parsedRows ? colValues(parsedRows) : inputData.split('\n').filter(Boolean)
            result = await generateFlowchart({ steps }, opts)
            break
          }
          case 'mindmap': {
            const text = parsedRows ? colValues(parsedRows).join('\n') : inputData
            result = await generateMindmap({ text }, opts)
            break
          }
          case 'org_chart':
            result = await generateOrgChart(parsedRows || JSON.parse(inputData), opts)
            break
          case 'timeline': {
            const events = parsedRows || inputData.split('\n').filter(Boolean)
            result = await generateTimeline({ events }, opts)
            break
          }
          case 'gantt':
            result = await generateGantt(parsedRows || JSON.parse(inputData), opts)
            break
          case 'kanban': {
            if (parsedRows) {
              result = await generateKanban({ items: parsedRows }, opts)
            } else {
              result = await generateKanban({ tasks: inputData }, opts)
            }
            break
          }
          case 'network': {
            if (parsedRows) {
              result = await generateNetworkGraph({ relationships: parsedRows }, opts)
            } else {
              result = await generateNetworkGraph({ connections: inputData.split('\n').filter(Boolean) }, opts)
            }
            break
          }
          case 'sequence': {
            if (parsedRows) {
              result = await generateSequenceDiagram({ interactions: parsedRows }, opts)
            } else {
              result = await generateSequenceDiagram({ interactions: inputData.split('\n').filter(Boolean) }, opts)
            }
            break
          }
          case 'wordcloud': {
            if (parsedRows) {
              const text = colValues(parsedRows).join(' ')
              result = await generateWordcloud({ text }, opts)
            } else {
              try {
                const parsed = JSON.parse(inputData)
                result = await generateWordcloud({ frequencies: parsed }, opts)
              } catch {
                result = await generateWordcloud({ text: inputData }, opts)
              }
            }
            break
          }
          default:
            break
        }

        if (result) {
          setPreviewType(selectedType.type)
          registerOutput({
            type: OutputType.DIAGRAM,
            title: `${selectedType.name}: ${title || 'Untitled'}`,
            summary: `${selectedType.name} diagram`,
            data: { id: result.id, svg: result.svg, mermaid: result.mermaid_code, content: result.content },
            format: 'diagram',
          })
          toast.show('Diagram generated', 'success')
        }
        return result
      } catch (err) {
        toast.show(`Error: ${err.message}`, 'error')
        throw err
      }
    }

    return execute({
      type: InteractionType.CREATE,
      label: `Generate ${selectedType.name}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      intent: { source: 'visualization', type: selectedType.type },
      action: generateAction,
    })
  }, [execute, generateFlowchart, generateGantt, generateKanban, generateMindmap, generateNetworkGraph, generateOrgChart, generateSequenceDiagram, generateTimeline, generateWordcloud, inputData, options, registerOutput, selectedType, title, toast])

  const handleExport = useCallback(async (format) => {
    if (!activeDiagram?.id) return

    let result
    switch (format) {
      case 'mermaid':
        result = await exportAsMermaid(activeDiagram.id)
        if (result) {
          navigator.clipboard.writeText(result.code)
          toast.show('Mermaid code copied', 'success')
        }
        break
      case 'svg':
        result = await exportAsSvg(activeDiagram.id)
        break
      case 'png':
        result = await exportAsPng(activeDiagram.id)
        if (result) {
          const url = URL.createObjectURL(result)
          const a = document.createElement('a')
          a.href = url
          a.download = `${title || 'diagram'}.png`
          a.click()
          URL.revokeObjectURL(url)
          toast.show('PNG downloaded', 'success')
        }
        break
      default:
        break
    }
  }, [activeDiagram?.id, exportAsMermaid, exportAsPng, exportAsSvg, title, toast])

  return {
    // Store state
    generating,
    error,

    // Local state
    selectedConnectionId,
    setSelectedConnectionId,
    selectedType,
    inputData,
    setInputData,
    title,
    setTitle,
    uploadingFile,
    uploadedFileName,
    extractedTable,
    activeDiagram,
    fileInputRef,

    // Handlers
    handleTypeChange,
    handleFileUpload,
    handleGenerate,
    handleExport,
  }
}
