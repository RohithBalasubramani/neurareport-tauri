import { describe, expect, beforeEach, afterEach, it, vi } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ThemeProvider } from '@mui/material/styles'

import TemplatePicker from '@/features/generate/components/TemplatePicker.jsx'
import theme from '@/app/theme.js'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import { useAppStore } from '@/stores'
import { recommendTemplates } from '@/api/client'

vi.mock('@tanstack/react-query', () => ({
  useQuery: () => ({ data: undefined, isLoading: false, isFetching: false, isError: false, error: null }),
  useQueryClient: () => ({ invalidateQueries: vi.fn(), setQueryData: vi.fn() }),
}))

vi.mock('@/api/client', () => {
  const recommendTemplatesMock = vi.fn(async () => [])
  return {
    isMock: false,
    withBase: (url) => url,
    deleteTemplate: vi.fn(),
    importTemplateZip: vi.fn(),
    fetchTemplateKeyOptions: vi.fn(),
    listApprovedTemplates: vi.fn(),
    getTemplateCatalog: vi.fn(),
    templateExportZipUrl: (id) => `/templates/${id}/export.zip`,
    recommendTemplates: recommendTemplatesMock,
    discoverReports: vi.fn(),
    runReport: vi.fn(),
    normalizeRunArtifacts: vi.fn(),
  }
})

const baseTemplate = {
  status: 'approved',
  artifacts: {},
  generator: {},
  mappingKeys: [],
  tags: [],
}

const companyTemplates = [
  {
    ...baseTemplate,
    id: 'comp-rec',
    name: 'Company Insights',
    domain: 'Finance',
    tags: ['finance'],
    source: 'company',
  },
]

const starterTemplates = [
  {
    ...baseTemplate,
    id: 'starter-rec',
    name: 'Starter Analysis',
    domain: 'Marketing',
    tags: ['marketing'],
    source: 'starter',
    description: 'Starter marketing summary.',
  },
]

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

describe('TemplatePicker recommended tab', () => {
  beforeEach(() => {
    useAppStore.setState((state) => ({
      ...state,
      templates: companyTemplates.map((tpl) => ({ ...tpl })),
      templateCatalog: [
        ...companyTemplates.map((tpl) => ({ ...tpl })),
        ...starterTemplates.map((tpl) => ({ ...tpl })),
      ],
    }))
  })

  afterEach(() => {
    cleanup()
    useAppStore.setState((state) => ({ ...state, templates: [], templateCatalog: [] }))
    vi.clearAllMocks()
  })

  it('renders company and starter recommendations with source chips and hints', async () => {
    const user = userEvent.setup()
    recommendTemplates.mockResolvedValue([
      {
        template: { ...companyTemplates[0], tags: ['finance'], domain: 'Finance' },
        explanation: 'Matches your finance requirement.',
        score: 0.9,
      },
      {
        template: { ...starterTemplates[0], tags: ['marketing'] },
        explanation: 'Starter overview for marketing.',
        score: 0.7,
      },
    ])
    renderPicker()

    const needInput = screen.getByLabelText('Describe what you need')
    await user.type(needInput, 'Need a finance summary')
    await user.click(screen.getByRole('button', { name: 'Get recommendations' }))

    expect(await screen.findByText('Company Insights')).toBeInTheDocument()
    expect(screen.getByText('Starter Analysis')).toBeInTheDocument()
    expect(screen.getAllByText('Company')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Starter')[0]).toBeInTheDocument()
    expect(screen.getByText('Starter marketing summary.')).toBeInTheDocument()
    expect(screen.getByText(/Starter template/)).toBeInTheDocument()
    expect(screen.getByText('Matches your finance requirement.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Find in "All" templates' })).toBeInTheDocument()
  })

  it('Find in "All" templates switches tabs and filters company list', async () => {
    const user = userEvent.setup()
    recommendTemplates.mockResolvedValue([
      {
        template: { ...companyTemplates[0], tags: ['finance'] },
        explanation: 'Company rec.',
        score: 0.9,
      },
    ])
    renderPicker()

    const needInput = screen.getByLabelText('Describe what you need')
    await user.type(needInput, 'Need finance')
    await user.click(screen.getByRole('button', { name: 'Get recommendations' }))
    await user.click(await screen.findByRole('button', { name: 'Find in "All" templates' }))

    const allTab = screen.getByRole('tab', { name: /^All$/ })
    expect(allTab).toHaveAttribute('aria-selected', 'true')

    const searchInput = screen.getByLabelText('Search by name')
    expect(searchInput).toHaveValue('Company Insights')
    expect(screen.getByText('Company templates')).toBeInTheDocument()
    expect(screen.getByText('Starter templates')).toBeInTheDocument()
  })
})
