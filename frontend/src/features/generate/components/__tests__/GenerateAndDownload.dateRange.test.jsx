import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import GenerateAndDownload from '../GenerateAndDownload.jsx'
import theme from '@/app/theme.js'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import { InteractionProvider } from '@/components/ux/governance'

vi.mock('@/hooks/useJobs', () => ({
  useTrackedJobs: () => ({ jobsById: {} }),
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

vi.mock('@/stores', () => ({
  useAppStore: (selector = (state) => state) => selector({ downloads: [] }),
}))

describe('GenerateAndDownload date range display', () => {
  const template = { id: 'tpl-1', name: 'Template 1', mappingKeys: [], artifacts: {}, generator: {} }
  const dateRange = { start: '2024-01-01', end: '2024-01-31', time_start: '2024-01-02', time_end: '2024-01-30' }

  it('shows discovered date range for active template', () => {
    const queryClient = new QueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <OperationHistoryProvider>
            <InteractionProvider>
              <GenerateAndDownload
            selected={['tpl-1']}
            selectedTemplates={[template]}
            autoType="PDF"
            start="2024-01-01"
            end="2024-01-31"
            setStart={() => {}}
            setEnd={() => {}}
            onFind={() => {}}
            findDisabled={false}
            finding={false}
            results={{
              'tpl-1': {
                batches: [],
                numericBins: {},
                dateRange,
                resample: { config: { dimension: 'time', metric: 'rows' } },
              },
            }}
            onToggleBatch={() => {}}
            onGenerate={() => {}}
            canGenerate={false}
            generateLabel="Run"
            generation={{ items: [] }}
            generatorReady
            generatorIssues={{ missing: [], needsFix: [], messages: [] }}
            keyValues={{}}
            onKeyValueChange={() => {}}
            keysReady
            keyOptions={{}}
            keyOptionsLoading={{}}
            onResampleFilter={() => {}}
              />
            </InteractionProvider>
          </OperationHistoryProvider>
        </ThemeProvider>
      </QueryClientProvider>,
    )

    expect(screen.getByText(/Range: 2024-01-01 → 2024-01-31/i)).toBeInTheDocument()
    expect(screen.getByText(/data 2024-01-02 → 2024-01-30/i)).toBeInTheDocument()
  })
})
