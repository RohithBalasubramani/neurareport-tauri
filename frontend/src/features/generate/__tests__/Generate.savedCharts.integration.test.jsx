import { describe, it, beforeEach, expect, vi } from 'vitest'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import GeneratePage from '@/features/generate/containers/GeneratePageContainer'
import theme from '@/app/theme.js'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import { InteractionProvider } from '@/components/ux/governance'
import { useAppStore } from '@/stores'

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

const {
  savedChartsStore,
  templatesMock,
  discoveryMock,
  suggestionMock,
  discoverReportsMock,
  suggestChartsMock,
  mockApiImplementation,
} = vi.hoisted(() => {
  const savedChartsStore = []
  const discovery = {
    batches: [
      { id: 'b1', rows: 120, parent: 12, selected: true },
      { id: 'b2', rows: 95, parent: 10, selected: true },
    ],
    batches_count: 2,
    rows_total: 215,
    field_catalog: [
      { name: 'batch_index', type: 'numeric', source: 'computed' },
      { name: 'batch_id', type: 'categorical', source: 'computed' },
      { name: 'rows', type: 'numeric', source: 'child_rows' },
      { name: 'parent', type: 'numeric', source: 'parent_rows' },
      { name: 'rows_per_parent', type: 'numeric', source: 'computed' },
      { name: 'time', type: 'time', source: 'computed' },
      { name: 'category', type: 'categorical', source: 'computed' },
    ],
    batch_metrics: [
      { batch_index: 1, batch_id: 'b1', rows: 120, parent: 12, rows_per_parent: 10 },
      { batch_index: 2, batch_id: 'b2', rows: 95, parent: 10, rows_per_parent: 9.5 },
    ],
  }
  const suggestion = {
    charts: [
      {
        id: 'chart-sugg-1',
        type: 'bar',
        xField: 'batch_index',
        yFields: ['rows'],
        title: 'Rows snapshot',
        description: 'bar chart preview',
        chartTemplateId: 'time_series_basic',
      },
    ],
    sampleData: [
      { batch_index: 1, rows: 120, parent: 12, rows_per_parent: 10 },
      { batch_index: 2, rows: 95, parent: 10, rows_per_parent: 9.5 },
    ],
  }
  const templatesMock = [
    {
      id: 'tpl-int',
      name: 'Integration Template',
      status: 'approved',
      kind: 'pdf',
      artifacts: {
        generator_sql_pack_url: '/mock.sql',
        generator_output_schemas_url: '/mock.json',
      },
      generator: { summary: {} },
      mappingKeys: [],
    },
  ]
  const discoverReportsMock = vi.fn().mockResolvedValue(discovery)
  const suggestChartsMock = vi.fn().mockResolvedValue(suggestion)
  const mockApiImplementation = {
    isMock: false,
    listApprovedTemplates: vi.fn().mockResolvedValue(templatesMock),
    fetchTemplateKeyOptions: vi.fn().mockResolvedValue({}),
    discoverReports: discoverReportsMock,
    suggestCharts: suggestChartsMock,
    listSavedCharts: vi.fn().mockImplementation(({ templateId }) =>
      Promise.resolve(
        savedChartsStore
          .filter((chart) => chart.templateId === templateId)
          .map((chart) => ({
            ...chart,
            spec: { ...chart.spec },
          })),
      ),
    ),
    createSavedChart: vi.fn().mockImplementation(({ templateId, name }) => {
      const record = {
        id: `saved-${savedChartsStore.length + 1}`,
        templateId,
        name,
        spec: {
          type: 'line',
          xField: 'missing_field',
          yFields: ['missing_metric'],
          chartTemplateId: 'time_series_basic',
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
      savedChartsStore.push(record)
      return Promise.resolve({ ...record, spec: { ...record.spec } })
    }),
    updateSavedChart: vi.fn().mockImplementation(({ templateId, chartId, name, spec }) => {
      const record = savedChartsStore.find((item) => item.id === chartId && item.templateId === templateId)
      if (!record) {
        throw new Error('Chart not found')
      }
      if (name != null) record.name = name
      if (spec != null) record.spec = { ...spec }
      record.updatedAt = new Date().toISOString()
      return Promise.resolve({ ...record, spec: { ...record.spec } })
    }),
    deleteSavedChart: vi.fn().mockImplementation(({ templateId, chartId }) => {
      const index = savedChartsStore.findIndex((item) => item.id === chartId && item.templateId === templateId)
      if (index >= 0) {
        savedChartsStore.splice(index, 1)
      }
      return Promise.resolve({ status: 'ok' })
    }),
  }
  return {
    savedChartsStore,
    templatesMock,
    discoveryMock: discovery,
    suggestionMock: suggestion,
    discoverReportsMock,
    suggestChartsMock,
    mockApiImplementation,
  }
})

vi.mock('@/api/client', async () => {
  const actual = await vi.importActual('@/api/client')
  return {
    ...actual,
    ...mockApiImplementation,
  }
})

// Also mock generateApi.js since some components import from there
vi.mock('@/features/generate/services/generateApi', async () => {
  const actual = await vi.importActual('@/features/generate/services/generateApi')
  return {
    ...actual,
    ...mockApiImplementation,
  }
})

const renderGeneratePage = () => {
  const queryClient = new QueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <OperationHistoryProvider>
          <InteractionProvider>
            <ToastProvider>
              <MemoryRouter initialEntries={['/generate']}>
                <Routes>
                  <Route path="/generate" element={<GeneratePage />} />
                </Routes>
              </MemoryRouter>
            </ToastProvider>
          </InteractionProvider>
        </OperationHistoryProvider>
      </ThemeProvider>
    </QueryClientProvider>,
  )
}

describe('GeneratePage saved chart integration', () => {
  beforeEach(() => {
    savedChartsStore.length = 0
    useAppStore.setState((state) => ({
      ...state,
      templates: templatesMock,
      selectedTemplates: [],
      savedConnections: [{ id: 'conn-1', name: 'Test Connection' }],
      lastUsed: {},
    }))
  })

  it(
    'saves a suggested chart, shows warning for invalid fields, and deletes it',
    async () => {
    const promptSpy = vi.spyOn(window, 'prompt').mockReturnValue('My saved chart')
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)

    renderGeneratePage()

    const templateTitle = await screen.findByText('Integration Template')
    const templateCard = templateTitle.closest('.MuiCard-root')
    expect(templateCard).toBeTruthy()
    const selectButton = within(templateCard).getByRole('button', { name: /^Select$/i })
    fireEvent.click(selectButton)
    await waitFor(() =>
      expect(within(templateCard).getByRole('button', { name: /^Selected$/i })).toBeInTheDocument(),
    )

    fireEvent.change(screen.getByLabelText(/Start Date & Time/i), { target: { value: '2024-01-01T00:00' } })
    fireEvent.change(screen.getByLabelText(/End Date & Time/i), { target: { value: '2024-01-02T00:00' } })

    const findButton = await screen.findByRole('button', { name: /Preview Data/i })
    await waitFor(() => expect(findButton).not.toBeDisabled(), { timeout: 3000 })
    fireEvent.click(findButton)
    await waitFor(() => expect(discoverReportsMock).toHaveBeenCalled())

    fireEvent.change(screen.getByLabelText(/Ask a question about this template's data/i), {
      target: { value: 'Show me trends' },
    })
    fireEvent.click(screen.getByRole('button', { name: /Ask AI for charts/i }))
    await screen.findByText('Rows snapshot')

    fireEvent.click(screen.getByRole('button', { name: /Save this chart/i }))
    await screen.findByText('My saved chart')
    await screen.findByText(/From template: time_series_basic/i)

    const savedCard = await screen.findByTestId('saved-chart-card-saved-1')
    fireEvent.click(savedCard)

    await screen.findByText(/Saved chart references fields not present/i)

    const deleteButton = within(savedCard).getByLabelText('Delete saved chart')
    fireEvent.click(deleteButton)

    await waitFor(() => expect(screen.queryByText('My saved chart')).not.toBeInTheDocument())
    await waitFor(() =>
      expect(screen.queryByText(/Saved chart references fields not present/i)).not.toBeInTheDocument(),
    )

    promptSpy.mockRestore()
    confirmSpy.mockRestore()
  },
  10000)
})
