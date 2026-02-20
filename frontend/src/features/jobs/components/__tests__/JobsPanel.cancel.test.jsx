import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ThemeProvider } from '@mui/material/styles'

import JobsPanel from '../JobsPanel.jsx'
import theme from '@/app/theme.js'
import { useAppStore } from '@/stores'
import { MemoryRouter } from 'react-router-dom'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import { InteractionProvider } from '@/components/ux/governance'

const setQueryData = vi.fn()
const getQueriesData = vi.fn(() => [])
vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({
    getQueriesData,
    setQueryData,
  }),
}))

const mockUseJobsList = vi.fn()
vi.mock('@/hooks/useJobs', () => ({
  useJobsList: (...args) => mockUseJobsList(...args),
}))

vi.mock('@/api/client', () => ({
  cancelJob: vi.fn(),
}))

describe('JobsPanel cancel', () => {
  const activeJob = {
    id: 'job-1',
    status: 'running',
    templateId: 'tpl-1',
    templateName: 'Template 1',
    templateKind: 'pdf',
    connectionId: 'conn-1',
    progress: 50,
    steps: [],
  }

  beforeEach(() => {
    setQueryData.mockReset()
    getQueriesData.mockReset()
    getQueriesData.mockReturnValue([])
    useAppStore.setState((state) => ({
      ...state,
      savedConnections: [{ id: 'conn-1', name: 'Conn One' }],
    }))
    mockUseJobsList.mockReturnValue({
      data: { jobs: [activeJob] },
      isLoading: false,
      isFetching: false,
      error: null,
      refetch: vi.fn(),
    })
  })

  it('renders cancel button for active job', async () => {
    const user = userEvent.setup()
    const { cancelJob } = await import('@/api/client')
    const refetchSpy = vi.fn()
    mockUseJobsList.mockReturnValue({
      data: { jobs: [activeJob] },
      isLoading: false,
      isFetching: false,
      error: null,
      refetch: refetchSpy,
    })

    render(
      <MemoryRouter>
        <ThemeProvider theme={theme}>
          <OperationHistoryProvider>
            <InteractionProvider>
              <JobsPanel open onClose={() => {}} />
            </InteractionProvider>
          </OperationHistoryProvider>
        </ThemeProvider>
      </MemoryRouter>,
    )

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)
    expect(cancelJob).toHaveBeenCalledWith('job-1', { force: false })
  })

  it('allows force cancelling a running job', async () => {
    const user = userEvent.setup()
    const { cancelJob } = await import('@/api/client')
    render(
      <MemoryRouter>
        <ThemeProvider theme={theme}>
          <OperationHistoryProvider>
            <InteractionProvider>
              <JobsPanel open onClose={() => {}} />
            </InteractionProvider>
          </OperationHistoryProvider>
        </ThemeProvider>
      </MemoryRouter>,
    )

    const forceButton = screen.getByRole('button', { name: /force stop/i })
    await user.click(forceButton)
    expect(cancelJob).toHaveBeenCalledWith('job-1', { force: true })
  })
})
