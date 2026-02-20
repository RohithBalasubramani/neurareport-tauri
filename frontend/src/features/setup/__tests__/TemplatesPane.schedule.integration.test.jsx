import { describe, it, beforeEach, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import dayjs from 'dayjs'

import TemplatesPane from '@/features/setup/containers/TemplatesPaneContainer'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import { InteractionProvider } from '@/components/ux/governance'
import theme from '@/app/theme.js'
import { useAppStore } from '@/stores'

const listSchedulesMock = vi.fn()
const createScheduleMock = vi.fn()

vi.mock('@/api/client', () => ({
  fetchTemplateKeyOptions: vi.fn(),
  discoverReports: vi.fn(),
  runReportAsJob: vi.fn(),
  listSchedules: (...args) => listSchedulesMock(...args),
  createSchedule: (...args) => createScheduleMock(...args),
  deleteSchedule: vi.fn(),
}))

vi.mock('@/features/generate/components/TemplatePicker', () => ({
  default: ({ onToggle }) => (
    <button type="button" onClick={() => onToggle('tpl-1')}>
      Select Template
    </button>
  ),
}))

vi.mock('@/features/generate/components/GenerateAndDownload', () => ({
  default: ({ setStart, setEnd }) => (
    <div>
      <button type="button" onClick={() => setStart(dayjs('2024-01-01T00:00'))}>
        Set start
      </button>
      <button type="button" onClick={() => setEnd(dayjs('2024-01-02T00:00'))}>
        Set end
      </button>
    </div>
  ),
}))

const renderPane = () =>
  render(
    <MemoryRouter>
      <ThemeProvider theme={theme}>
        <OperationHistoryProvider>
          <InteractionProvider>
            <ToastProvider>
              <TemplatesPane />
            </ToastProvider>
          </InteractionProvider>
        </OperationHistoryProvider>
      </ThemeProvider>
    </MemoryRouter>,
  )

describe('TemplatesPane scheduling flows', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useAppStore.setState((state) => ({
      ...state,
      templates: [
        {
          id: 'tpl-1',
          name: 'Template One',
          status: 'approved',
          kind: 'pdf',
          mappingKeys: [],
        },
      ],
      activeConnectionId: 'conn-1',
      activeConnection: { id: 'conn-1', name: 'Primary DB' },
      discoveryResults: {},
      discoveryMeta: null,
      discoveryFinding: false,
    }))
    listSchedulesMock.mockReset()
    createScheduleMock.mockReset()
  })

  it('creates a schedule and refreshes the list', async () => {
    const scheduled = [{
      id: 'sch-1',
      name: 'Nightly run',
      template_id: 'tpl-1',
      template_name: 'Template One',
      frequency: 'daily',
      next_run_at: '2024-01-03T00:00:00Z',
    }]
    listSchedulesMock.mockImplementation(() => Promise.resolve(scheduled))
    listSchedulesMock.mockImplementationOnce(() => Promise.resolve([]))
    createScheduleMock.mockResolvedValue({ id: 'sch-1' })

    renderPane()

    await userEvent.click(screen.getByRole('button', { name: /select template/i }))

    await userEvent.click(screen.getByRole('tab', { name: /configure/i }))
    await userEvent.click(screen.getByRole('button', { name: /set start/i }))
    await userEvent.click(screen.getByRole('button', { name: /set end/i }))

    await userEvent.click(screen.getByRole('tab', { name: /schedules/i }))
    await screen.findByText(/No schedules yet/i)

    const scheduleButton = screen.getByRole('button', { name: /create schedule/i })
    expect(scheduleButton).not.toBeDisabled()
    await userEvent.click(scheduleButton)

    await waitFor(() => expect(createScheduleMock).toHaveBeenCalled())
    expect(createScheduleMock).toHaveBeenCalledWith(
      expect.objectContaining({
        templateId: 'tpl-1',
        connectionId: 'conn-1',
        startDate: '2024-01-01 00:00:00',
        endDate: '2024-01-02 00:00:00',
        frequency: 'daily',
      }),
    )

    await waitFor(() => expect(listSchedulesMock.mock.calls.length).toBeGreaterThanOrEqual(2))
    await screen.findByText(/Nightly run/i)
    expect(screen.getByText(/Next:/i)).toBeInTheDocument()
  })
})
