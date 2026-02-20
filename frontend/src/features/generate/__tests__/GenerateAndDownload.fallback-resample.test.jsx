import { describe, it, expect, beforeEach, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@mui/material/styles'
import { MemoryRouter } from 'react-router-dom'

import GenerateAndDownload from '@/features/generate/components/GenerateAndDownload.jsx'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import { InteractionProvider } from '@/components/ux/governance'
import theme from '@/app/theme.js'
import { useAppStore } from '@/stores'
import { DEFAULT_RESAMPLE_CONFIG } from '@/features/generate/utils/generateFeatureUtils.js'

const { suggestChartsMock } = vi.hoisted(() => ({
  suggestChartsMock: vi.fn(),
}))

vi.mock('@/features/generate/services/generateApi', () => ({
  suggestCharts: (...args) => suggestChartsMock(...args),
  createSavedChart: vi.fn(),
  deleteSavedChart: vi.fn(),
  withBase: (url) => url,
}))

vi.mock('@/features/generate/hooks/useSavedCharts', () => ({
  useSavedCharts: () => ({
    savedCharts: [],
    savedChartsLoading: false,
    savedChartsError: null,
    fetchSavedCharts: vi.fn(),
    createSavedChart: vi.fn(),
    renameSavedChart: vi.fn(),
    deleteSavedChart: vi.fn(),
  }),
}))

vi.mock('@/hooks/useJobs', () => ({
  useTrackedJobs: () => ({ jobsById: {}, isFetching: false }),
}))

vi.mock('recharts', () => {
  const React = require('react')
  const passthrough = (name) => ({ children }) =>
    React.createElement('div', { 'data-testid': name }, children)
  const Chart = ({ data, type, children }) => (
    <div data-testid={`${type}-chart`}>
      {(data || []).map((row, idx) => (
        <div key={`${type}-${idx}`} data-testid={`${type}-point`}>
          {JSON.stringify(row)}
        </div>
      ))}
      {children}
    </div>
  )
  const Brush = ({ onChange }) => (
    <button
      type="button"
      data-testid="recharts-brush"
      onClick={() => onChange?.({ startIndex: 1, endIndex: 1 })}
    >
      Brush
    </button>
  )
  return {
    ResponsiveContainer: passthrough('responsive-container'),
    BarChart: ({ data, children }) => <Chart type="bar" data={data}>{children}</Chart>,
    Bar: passthrough('bar'),
    LineChart: ({ data, children }) => <Chart type="line" data={data}>{children}</Chart>,
    Line: passthrough('line'),
    PieChart: ({ children }) => <div data-testid="pie-chart">{children}</div>,
    Pie: passthrough('pie'),
    Cell: passthrough('cell'),
    ScatterChart: ({ children }) => <div data-testid="scatter-chart">{children}</div>,
    Scatter: passthrough('scatter'),
    CartesianGrid: passthrough('cartesian-grid'),
    XAxis: ({ dataKey }) => <div data-testid={`x-axis-${dataKey}`} />,
    YAxis: ({ dataKey }) => <div data-testid={`y-axis-${dataKey || 'value'}`} />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />,
    Brush,
  }
})

if (!global.ResizeObserver) {
  vi.stubGlobal(
    'ResizeObserver',
    class {
      observe() {}
      unobserve() {}
      disconnect() {}
    },
  )
}

const baseTemplate = {
  id: 'tpl-1',
  name: 'Template One',
  kind: 'pdf',
  mappingKeys: [],
}

const baseResults = {
  [baseTemplate.id]: {
    name: baseTemplate.name,
    batches: [
      { id: 'b1', rows: 10, parent: 2, time: '2024-01-01' },
      { id: 'b2', rows: 12, parent: 3, time: '2024-01-02' },
    ],
    allBatches: [
      { id: 'b1', rows: 10, parent: 2, time: '2024-01-01' },
      { id: 'b2', rows: 12, parent: 3, time: '2024-01-02' },
    ],
    batchMetrics: [
      { batch_index: 1, batch_id: 'b1', rows: 10, parent: 2, rows_per_parent: 5 },
      { batch_index: 2, batch_id: 'b2', rows: 12, parent: 3, rows_per_parent: 4 },
    ],
    fieldCatalog: [
      { name: 'rows', type: 'numeric' },
      { name: 'batch_index', type: 'numeric' },
    ],
    resample: { config: { ...DEFAULT_RESAMPLE_CONFIG } },
  },
}

const renderGenerateAndDownload = (overrides = {}) => {
  const queryClient = new QueryClient()
  const props = {
    selected: [baseTemplate.id],
    selectedTemplates: [baseTemplate],
    autoType: 'PDF',
    start: '2024-01-01T00:00',
    end: '2024-01-02T00:00',
    setStart: vi.fn(),
    setEnd: vi.fn(),
    onFind: vi.fn(),
    findDisabled: false,
    finding: false,
    results: overrides.results || baseResults,
    onToggleBatch: vi.fn(),
    onGenerate: vi.fn(),
    canGenerate: true,
    generateLabel: 'Run Reports',
    generation: { items: [] },
    generatorReady: true,
    generatorIssues: { missing: [], needsFix: [], messages: [] },
    keyValues: {},
    onKeyValueChange: vi.fn(),
    keysReady: true,
    keyOptions: {},
    keyOptionsLoading: {},
    onResampleFilter: vi.fn(),
    ...overrides,
  }
  return {
    ...render(
      <MemoryRouter>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <OperationHistoryProvider>
              <InteractionProvider>
                <ToastProvider>
                  <GenerateAndDownload {...props} />
                </ToastProvider>
              </InteractionProvider>
            </OperationHistoryProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </MemoryRouter>,
    ),
    props,
  }
}

describe('GenerateAndDownload chart behaviors', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useAppStore.setState((state) => ({ ...state, downloads: [], templates: [baseTemplate] }))
  })

  it('renders fallback chart suggestions with sample data when AI returns none', async () => {
    const sampleData = [
      { bucket: 'Group A', value: 5 },
      { bucket: 'Group B', value: 8 },
    ]
    suggestChartsMock.mockResolvedValue({ charts: [], sampleData })
    renderGenerateAndDownload()

    fireEvent.click(screen.getByRole('button', { name: /Ask AI for charts/i }))

    await screen.findByText('Line distribution')
    screen.getByText('Bar distribution')
    screen.getByText('Using sample dataset from suggestion response')
    const samplePoints = screen.getAllByTestId('line-point').map((node) => node.textContent || '')
    expect(samplePoints.some((text) => text.includes('"bucket":"Group B"'))).toBe(true)
  })

  it('applies numeric bin filtering from the resample brush', async () => {
    const onResampleFilter = vi.fn()
    const numericResults = {
      [baseTemplate.id]: {
        ...baseResults[baseTemplate.id],
        batchMetrics: [
          { batch_index: 1, batch_id: 'b1', score: 2 },
          { batch_index: 2, batch_id: 'b2', score: 8 },
          { batch_index: 3, batch_id: 'b3', score: 14 },
        ],
        numericBins: {
          score: [
            { start: 0, end: 5, count: 1, sum: 2, batch_ids: ['b1'] },
            { start: 5, end: 10, count: 1, sum: 8, batch_ids: ['b2'] },
            { start: 10, end: 15, count: 1, sum: 14, batch_ids: ['b3'] },
          ],
        },
        resample: {
          config: {
            ...DEFAULT_RESAMPLE_CONFIG,
            dimension: 'score',
            dimensionKind: 'numeric',
            metric: 'score',
            bucket: 'auto',
          },
        },
        discoverySchema: {
          dimensions: [{ name: 'score', kind: 'numeric', bucketable: true }],
          metrics: [{ name: 'score' }],
        },
      },
    }
    renderGenerateAndDownload({ onResampleFilter, results: numericResults })

    await screen.findByText(/0 - 5/)
    screen.getByText(/10 - 15/)

    fireEvent.click(screen.getByTestId('recharts-brush'))

    expect(onResampleFilter).toHaveBeenCalledWith(
      baseTemplate.id,
      expect.objectContaining({
        allowedBatchIds: ['b2'],
        config: expect.objectContaining({ range: [1, 1], dimension: 'score' }),
      }),
    )
  })

  it('renders category groups and filters allowed ids when brushing', async () => {
    const onResampleFilter = vi.fn()
    const categoryResults = {
      [baseTemplate.id]: {
        ...baseResults[baseTemplate.id],
        categoryGroups: {
          category: [
            { key: 'north', label: 'North', value: 12, batch_ids: ['b1', 'b2'] },
            { key: 'south', label: 'South', value: 7, batch_ids: ['b3'] },
          ],
        },
        batchMetrics: [
          { batch_index: 1, batch_id: 'b1', rows: 10, category: 'North' },
          { batch_index: 2, batch_id: 'b2', rows: 2, category: 'North' },
          { batch_index: 3, batch_id: 'b3', rows: 7, category: 'South' },
        ],
        resample: {
          config: {
            ...DEFAULT_RESAMPLE_CONFIG,
            dimension: 'category',
            dimensionKind: 'categorical',
            metric: 'rows',
          },
        },
        discoverySchema: {
          dimensions: [{ name: 'category', kind: 'categorical', bucketable: false }],
          metrics: [{ name: 'rows' }],
        },
        fieldCatalog: [
          { name: 'category', type: 'categorical' },
          { name: 'rows', type: 'numeric' },
        ],
      },
    }
    renderGenerateAndDownload({ results: categoryResults, onResampleFilter })

    const points = await screen.findAllByTestId('bar-point')
    expect(points.some((node) => (node.textContent || '').includes('North'))).toBe(true)
    expect(points.some((node) => (node.textContent || '').includes('South'))).toBe(true)

    fireEvent.click(screen.getByTestId('recharts-brush'))

    expect(onResampleFilter).toHaveBeenCalledWith(
      baseTemplate.id,
      expect.objectContaining({
        allowedBatchIds: ['b3'],
        config: expect.objectContaining({ dimension: 'category', range: [1, 1] }),
      }),
    )
  })
})
