import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import { MemoryRouter } from 'react-router-dom'
import theme from '@/app/theme.js'
import { useAppStore } from '@/stores'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import { InteractionProvider } from '@/components/ux/governance'
import JobsPanel from '../JobsPanel.jsx'

const mockUseJobsList = vi.fn()
const mockNavigate = vi.fn()
const setQueryData = vi.fn()
const getQueriesData = vi.fn(() => [])

vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({
    getQueriesData,
    setQueryData,
  }),
}))

vi.mock('@/hooks/useJobs', () => ({
  useJobsList: (...args) => mockUseJobsList(...args),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

const baseJobs = [
  {
    id: 'job-running',
    templateId: 'tpl-1',
    templateName: 'Template Alpha',
    status: 'running',
    type: 'run_report',
    templateKind: 'pdf',
    connectionId: 'conn-1',
    startedAt: '2025-01-02T10:00:00.000Z',
    progress: 60,
    meta: { start_date: '2025-01-01 00:00:00', end_date: '2025-01-07 00:00:00' },
    result: {},
    steps: [{ id: 'step-1', name: 'dataLoad', label: 'Load database', status: 'succeeded' }],
  },
  {
    id: 'job-complete',
    templateId: 'tpl-2',
    templateName: 'Template Beta',
    status: 'succeeded',
    type: 'run_report',
    templateKind: 'pdf',
    connectionId: 'conn-2',
    startedAt: '2025-01-01T09:00:00.000Z',
    finishedAt: '2025-01-01T09:30:00.000Z',
    progress: 100,
    meta: {
      start_date: '2025-01-01 00:00:00',
      end_date: '2025-01-15 00:00:00',
      errors: ['Missing filter token'],
    },
    result: { errors: ['PDF renderer warning'] },
    steps: [
      { id: 'step-2', name: 'dataLoad', label: 'DB load', status: 'succeeded' },
      { id: 'step-3', name: 'renderPdf', label: 'Render PDF', status: 'succeeded' },
    ],
  },
  {
    id: 'job-failed',
    templateId: 'tpl-3',
    templateName: 'Template Gamma',
    status: 'failed',
    error: 'Disk failure',
    type: 'run_report',
    templateKind: 'pdf',
    connectionId: 'conn-missing',
    meta: { start_date: '2025-01-03 00:00:00', errors: ['Meta validation failed'] },
    result: { error: 'Template script crashed' },
    steps: [{ id: 'step-4', name: 'dataLoad', label: 'Load database', status: 'failed' }],
  },
]

function renderJobsPanel({ jobs = baseJobs, overrides = {}, onClose = vi.fn() } = {}) {
  const queryResult = {
    data: { jobs },
    isLoading: false,
    isFetching: false,
    error: null,
    refetch: vi.fn(),
    ...overrides,
  }
  mockUseJobsList.mockReturnValue(queryResult)
  render(
    <MemoryRouter>
      <ThemeProvider theme={theme}>
        <OperationHistoryProvider>
          <InteractionProvider>
            <JobsPanel open onClose={onClose} />
          </InteractionProvider>
        </OperationHistoryProvider>
      </ThemeProvider>
    </MemoryRouter>,
  )
  return { onClose, refetch: queryResult.refetch }
}

describe('JobsPanel', () => {
  beforeEach(() => {
    mockUseJobsList.mockReset()
    mockNavigate.mockReset()
    setQueryData.mockReset()
    getQueriesData.mockReset()
    getQueriesData.mockReturnValue([])
    useAppStore.setState({
      savedConnections: [
        { id: 'conn-1', name: 'Primary Warehouse' },
        { id: 'conn-2', name: 'Finance DB' },
      ],
    })
  })

  it('renders jobs with status chips and errors', () => {
    renderJobsPanel()
    expect(screen.getAllByText('Template Alpha').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Template Beta').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Template Gamma').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Running').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Completed').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Failed').length).toBeGreaterThan(0)
    expect(screen.getByText('Disk failure')).toBeTruthy()
    expect(screen.getByText('Primary Warehouse')).toBeTruthy()
    expect(screen.getByText('Finance DB')).toBeTruthy()
    expect(screen.getByText('conn-missing')).toBeTruthy()
    expect(screen.getByText('2025-01-01 -> 2025-01-07')).toBeTruthy()
    expect(screen.getByText('2025-01-01 -> 2025-01-15')).toBeTruthy()
    expect(screen.getByText((text) => text.includes('Missing filter token'))).toBeTruthy()
    expect(screen.getByText((text) => text.includes('PDF renderer warning'))).toBeTruthy()
    expect(screen.getByText((text) => text.includes('Meta validation failed'))).toBeTruthy()
  })

  it('shows individual job steps for inspection', () => {
    renderJobsPanel()
    expect(screen.getAllByText('DB load').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Render PDF').length).toBeGreaterThan(0)
    // chip text for succeeded step should be visible alongside label
    expect(screen.getAllByText('Completed').length).toBeGreaterThan(1)
  })

  it('navigates to Reports when requested', () => {
    const { onClose } = renderJobsPanel()
    const card = screen.getByText('Template Beta').closest('[data-testid="job-card"]')
    expect(card).toBeTruthy()
    fireEvent.click(within(card).getByRole('button', { name: /Open Report/i }))
    expect(mockNavigate).toHaveBeenCalled()
    expect(mockNavigate.mock.calls[0][0]).toBe('/reports?template=tpl-2')
    expect(onClose).toHaveBeenCalled()
  })

  it('navigates to setup for the related connection', () => {
    const { onClose } = renderJobsPanel()
    const card = screen.getByText('Template Alpha').closest('[data-testid="job-card"]')
    expect(card).toBeTruthy()
    fireEvent.click(within(card).getByRole('button', { name: /Go to Setup/i }))
    expect(mockNavigate).toHaveBeenCalled()
    expect(mockNavigate.mock.calls[0][0]).toBe('/setup/wizard')
    expect(onClose).toHaveBeenCalled()
  })

  it('filters jobs by status chips', async () => {
    renderJobsPanel()
    const groups = screen.getAllByTestId('jobs-filter-group')
    const currentGroup = groups[groups.length - 1]
    const failedChip = within(currentGroup).getByTestId('jobs-filter-failed')
    fireEvent.click(failedChip)
    await waitFor(() => {
      const lists = screen.getAllByTestId('jobs-list')
      const currentList = lists[lists.length - 1]
      expect(within(currentList).queryByText('Template Alpha')).toBeNull()
      expect(within(currentList).getByText('Template Gamma')).toBeTruthy()
    })
  })

  it('shows empty and error states with retry', () => {
    const { refetch } = renderJobsPanel({
      jobs: [],
      overrides: { error: new Error('Network down') },
    })
    expect(screen.getByText('Failed to load jobs: Network down')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: /Retry/i }))
    expect(refetch).toHaveBeenCalled()

    renderJobsPanel({ jobs: [] })
    expect(screen.getByText('No jobs to display')).toBeTruthy()
  })

  it('shows scheduled jobs with steps and cancel option', () => {
    const scheduledJob = {
      id: 'job-scheduled',
      templateId: 'tpl-scheduled',
      templateName: 'Scheduled Template',
      status: 'running',
      type: 'schedule_run',
      templateKind: 'pdf',
      connectionId: 'conn-1',
      progress: 40,
      steps: [
        { id: 'step-1', name: 'queue', label: 'Queue', status: 'running' },
        { id: 'step-2', name: 'render', label: 'Render', status: 'queued' },
      ],
    }
    renderJobsPanel({ jobs: [scheduledJob] })

    const [card] = screen.getAllByTestId('job-card')
    expect(within(card).getByText(/Scheduled Template/i)).toBeTruthy()
    expect(within(card).getByText(/schedule run/i)).toBeTruthy()
    expect(within(card).getByText('Queue')).toBeTruthy()
    expect(within(card).getByRole('button', { name: /Cancel/i })).toBeTruthy()
  })
})
