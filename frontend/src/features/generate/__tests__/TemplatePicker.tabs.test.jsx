import { describe, expect, beforeEach, afterEach, it, vi } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ThemeProvider } from '@mui/material/styles'

import TemplatePicker from '@/features/generate/components/TemplatePicker.jsx'
import theme from '@/app/theme.js'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import { useAppStore } from '@/stores'

vi.mock('@tanstack/react-query', () => ({
  useQuery: () => ({ data: undefined, isLoading: false, isFetching: false, isError: false, error: null }),
  useQueryClient: () => ({ invalidateQueries: vi.fn(), setQueryData: vi.fn() }),
}))

vi.mock('@/api/client', () => ({
  isMock: false,
  withBase: (url) => url,
  deleteTemplate: vi.fn(),
  importTemplateZip: vi.fn(),
  fetchTemplateKeyOptions: vi.fn(async () => ({ keys: {} })),
  listApprovedTemplates: vi.fn(async () => []),
  getTemplateCatalog: vi.fn(async () => []),
  templateExportZipUrl: (id) => `/templates/${id}/export.zip`,
  recommendTemplates: vi.fn(async () => []),
  discoverReports: vi.fn(),
  runReport: vi.fn(),
  normalizeRunArtifacts: vi.fn(),
}))

const baseTemplate = {
  status: 'approved',
  artifacts: {},
  generator: {},
  mappingKeys: [],
  tags: [],
}

const companySeeds = [
  {
    ...baseTemplate,
    id: 'comp-1',
    name: 'Revenue Pulse',
    domain: 'Finance',
    tags: ['finance'],
    source: 'company',
  },
  {
    ...baseTemplate,
    id: 'comp-2',
    name: 'Ops Health',
    domain: 'Operations',
    tags: ['ops'],
    source: 'company',
  },
]

const starterSeeds = [
  {
    ...baseTemplate,
    id: 'starter-1',
    name: 'Starter Marketing Playbook',
    domain: 'Marketing',
    tags: ['marketing'],
    source: 'starter',
    description: 'Marketing best practices starter template.',
  },
  {
    ...baseTemplate,
    id: 'starter-2',
    name: 'Starter Ops Dashboard',
    domain: 'Operations',
    tags: ['ops'],
    source: 'starter',
    description: 'Operations snapshot starter template.',
  },
]

const cloneTemplates = (templates) => templates.map((tpl) => ({ ...tpl, artifacts: {}, generator: {}, mappingKeys: [], tags: [...(tpl.tags || [])] }))

const renderPicker = () =>
  render(
    <ThemeProvider theme={theme}>
      <ToastProvider>
        <TemplatePicker
          selected={[]}
          onToggle={() => {}}
          outputFormats={{}}
          setOutputFormats={() => {}}
          tagFilter={[]}
          setTagFilter={() => {}}
          onEditTemplate={() => {}}
        />
      </ToastProvider>
    </ThemeProvider>,
  )

describe('TemplatePicker tabs', () => {
  beforeEach(() => {
    useAppStore.setState((state) => ({
      ...state,
      templates: cloneTemplates(companySeeds),
      templateCatalog: [...cloneTemplates(companySeeds), ...cloneTemplates(starterSeeds)],
    }))
  })

  afterEach(() => {
    useAppStore.setState((state) => ({ ...state, templates: [], templateCatalog: [] }))
  })

  it('All tab shows company and starter sections and filters both', async () => {
    const user = userEvent.setup()
    renderPicker()

    expect(screen.getByText('Company templates')).toBeInTheDocument()
    expect(screen.getByText('Starter templates')).toBeInTheDocument()
    expect(screen.getByLabelText('Select Revenue Pulse')).toBeInTheDocument()
    expect(screen.getByText('Starter Marketing Playbook')).toBeInTheDocument()
    expect(screen.queryByLabelText('Select Starter Marketing Playbook')).not.toBeInTheDocument()

    const searchInput = screen.getByLabelText('Search by name')
    await user.clear(searchInput)
    await user.type(searchInput, 'Ops')

    expect(screen.queryByText('Revenue Pulse')).not.toBeInTheDocument()
    expect(screen.getByText('Ops Health')).toBeInTheDocument()
    expect(screen.queryByText('Starter Marketing Playbook')).not.toBeInTheDocument()
    expect(screen.queryByText('Starter templates')).toBeNull()
  })

  it('Company tab shows only company templates with selection controls', async () => {
    const user = userEvent.setup()
    renderPicker()

    await user.click(screen.getByRole('tab', { name: /^Company$/ }))

    expect(screen.queryByText('Starter templates')).toBeNull()
    expect(screen.getAllByLabelText('Output format').length).toBeGreaterThan(0)
    expect(screen.getByLabelText('Select Revenue Pulse')).toBeInTheDocument()
    expect(screen.getByLabelText('Select Ops Health')).toBeInTheDocument()
  })

  it('Starter tab renders read-only starter cards', async () => {
    const user = userEvent.setup()
    renderPicker()

    await user.click(screen.getByRole('tab', { name: /^Starter$/ }))
    expect(screen.getByText('Starter Marketing Playbook')).toBeInTheDocument()
    expect(screen.queryByLabelText('Select Starter Marketing Playbook')).toBeNull()
  })

  it('Starter tab shows empty state when no starter templates exist', async () => {
    useAppStore.setState((state) => ({ ...state, templateCatalog: cloneTemplates(companySeeds) }))
    const user = userEvent.setup()
    renderPicker()

    await user.click(screen.getByRole('tab', { name: /^Starter$/ }))
    expect(screen.getByText('No starter templates available')).toBeInTheDocument()
  })
})
