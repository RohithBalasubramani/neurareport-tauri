import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import { useState } from 'react'
import { ThemeProvider } from '@mui/material/styles'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query'
import theme from '@/app/theme.js'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import { InteractionProvider } from '@/components/ux/governance'

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    MemoryRouter: actual.MemoryRouter,
  }
})

// Mock the UX governance hooks to avoid context issues with dynamic imports
vi.mock('@/components/ux/governance', () => ({
  InteractionProvider: ({ children }) => children,
  useInteraction: () => ({
    execute: async (contract) => {
      // Execute the action and return the result
      if (contract.action) {
        return contract.action()
      }
      return {}
    },
    start: vi.fn().mockResolvedValue({}),
    handleUserAction: vi.fn().mockResolvedValue({}),
    handleBackendResponse: vi.fn().mockResolvedValue({}),
    isExecuting: false,
    currentIntent: null,
  }),
  useNavigateInteraction: () => vi.fn(),
  InteractionType: {
    CREATE: 'create',
    UPDATE: 'update',
    DELETE: 'delete',
    UPLOAD: 'upload',
    DOWNLOAD: 'download',
    GENERATE: 'generate',
    ANALYZE: 'analyze',
    EXECUTE: 'execute',
    NAVIGATE: 'navigate',
    LOGIN: 'login',
    LOGOUT: 'logout',
  },
  Reversibility: {
    FULLY_REVERSIBLE: 'fully_reversible',
    PARTIALLY_REVERSIBLE: 'partially_reversible',
    IRREVERSIBLE: 'irreversible',
    SYSTEM_MANAGED: 'system_managed',
  },
  FeedbackType: {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info',
  },
}))

let JobsPanel
let runReportAsJobFn
let runReportAsJobSpy
let GenerateAndDownload

const readyTemplate = {
  id: 'tpl_generate_job',
  name: 'Quarterly Revenue (Mock)',
  status: 'approved',
  tags: ['finance'],
  kind: 'pdf',
  artifacts: {
    generator_sql_pack_url: '/mock/sql.pack',
    generator_output_schemas_url: '/mock/schema.json',
  },
  generator: {
    invalid: false,
    needsUserFix: [],
    updatedAt: '2024-01-01T00:00:00Z',
  },
}

beforeEach(
  async () => {
    vi.resetModules()
    globalThis.__NEURA_TEST_ENVIRONMENT__ = { VITE_USE_MOCK: 'true' }
    JobsPanel = (await import('@/features/jobs/components/JobsPanel.jsx')).default
    const clientModule = await import('@/api/client.js')
    const realRunReportAsJob = clientModule.runReportAsJob
    GenerateAndDownload = (await import('@/features/generate/components/GenerateAndDownload.jsx')).default
    runReportAsJobSpy = vi
      .spyOn(clientModule, 'runReportAsJob')
      .mockImplementation((payload) => realRunReportAsJob(payload))
    runReportAsJobFn = clientModule.runReportAsJob
    mockNavigate.mockReset()
  },
  20000,
)

afterEach(() => {
  vi.restoreAllMocks()
  delete globalThis.__NEURA_TEST_ENVIRONMENT__
})

function TestGenerateDriver() {
  const queryClient = useQueryClient()
  const [generation, setGeneration] = useState({ items: [] })
  const handleRun = async () => {
    const response = await runReportAsJobFn({
      templateId: readyTemplate.id,
      templateName: readyTemplate.name,
      startDate: '2024-01-01 00:00:00',
      endDate: '2024-01-01 12:00:00',
    })
    setGeneration({
      items: [
        {
          id: `driver-${Date.now()}`,
          tplId: readyTemplate.id,
          name: readyTemplate.name,
          kind: readyTemplate.kind,
          status: 'queued',
          progress: 10,
          jobId: response?.job_id || null,
          error: null,
        },
      ],
    })
    await queryClient.invalidateQueries({ queryKey: ['jobs'] })
  }
  return (
    <div>
      <button type="button" onClick={handleRun}>
        Run mock report
      </button>
      <GenerateAndDownload
        selected={[readyTemplate.id]}
        selectedTemplates={[readyTemplate]}
        autoType="PDF"
        start=""
        end=""
        setStart={() => {}}
        setEnd={() => {}}
        onFind={() => {}}
        findDisabled={false}
        finding={false}
        results={{}}
        onToggleBatch={() => {}}
        onGenerate={() => {}}
        canGenerate={false}
        generateLabel="Run Reports"
        generation={generation}
        generatorReady
        generatorIssues={{ ready: true, missing: [], needsFix: [], messages: [] }}
        keyValues={{}}
        onKeyValueChange={() => {}}
        keysReady
        keyOptions={{}}
        keyOptionsLoading={{}}
        onResampleFilter={() => {}}
      />
    </div>
  )
}

function TestShell({ queryClient }) {
  const [jobsOpen, setJobsOpen] = useState(false)
  return (
    <MemoryRouter initialEntries={['/generate']}>
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <OperationHistoryProvider>
            <InteractionProvider>
              <ToastProvider>
                <TestGenerateDriver />
                <button type="button" aria-label="Open jobs panel" onClick={() => setJobsOpen(true)}>
                  Open jobs panel
                </button>
                <JobsPanel open={jobsOpen} onClose={() => setJobsOpen(false)} />
              </ToastProvider>
            </InteractionProvider>
          </OperationHistoryProvider>
        </QueryClientProvider>
      </ThemeProvider>
    </MemoryRouter>
  )
}

describe('Generate to JobsPanel integration (mock mode)', () => {
  it('queues jobs from the Generate page and surfaces them in JobsPanel', async () => {
    const queryClient = new QueryClient()
    render(<TestShell queryClient={queryClient} />)

    fireEvent.click(screen.getByRole('button', { name: /Run mock report/i }))
    await waitFor(() => expect(runReportAsJobSpy).toHaveBeenCalledTimes(1))

    await screen.findByText(/Reports continue running in the background/i)

    fireEvent.click(screen.getByLabelText('Open jobs panel'))
    await waitFor(() => expect(screen.getByText('Background Jobs')).toBeTruthy())

    const lists = await screen.findAllByTestId('jobs-list')
    const currentList = lists[lists.length - 1]
    const jobHeadings = await within(currentList).findAllByText(readyTemplate.name, { exact: false }, { timeout: 8000 })
    const newJobCard = jobHeadings[0].closest('[data-testid="job-card"]')
    expect(newJobCard).toBeTruthy()
    expect(within(newJobCard).getAllByText(/Pending|Queued|Running/i).length).toBeGreaterThan(0)

    const completedHeadings = await within(currentList).findAllByText('Completed mock run')
    const completedCard = completedHeadings[0].closest('[data-testid="job-card"]')
    expect(completedCard).toBeTruthy()
    fireEvent.click(within(completedCard).getByRole('button', { name: /Open Report/i }))
    expect(mockNavigate).toHaveBeenCalled()
    expect(mockNavigate.mock.calls[0][0]).toBe('/reports?template=tpl_success_mock')
  }, 10000)
})
