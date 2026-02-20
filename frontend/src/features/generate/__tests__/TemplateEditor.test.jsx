import { describe, expect, beforeEach, afterEach, beforeAll, afterAll, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'

import TemplateEditor from '@/features/generate/containers/TemplateEditor'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import { InteractionProvider } from '@/components/ux/governance'
import theme from '@/app/theme.js'
import { useAppStore } from '@/stores'
import {
  getTemplateHtml,
  editTemplateManual,
  editTemplateAi,
  undoTemplateEdit,
} from '@/api/client'

vi.mock('@/api/client', () => ({
  getTemplateHtml: vi.fn(),
  editTemplateManual: vi.fn(),
  editTemplateAi: vi.fn(),
  undoTemplateEdit: vi.fn(),
}))

const baseTemplate = {
  id: 'tpl-1',
  name: 'Template One',
  status: 'approved',
  source: 'company',
  generator: { summary: {} },
}

const renderEditor = () =>
  render(
    <ThemeProvider theme={theme}>
      <OperationHistoryProvider>
        <InteractionProvider>
          <ToastProvider>
            <MemoryRouter initialEntries={['/templates/tpl-1/edit']}>
              <Routes>
                <Route path="/templates/:templateId/edit" element={<TemplateEditor />} />
              </Routes>
            </MemoryRouter>
          </ToastProvider>
        </InteractionProvider>
      </OperationHistoryProvider>
    </ThemeProvider>,
  )

describe('TemplateEditor metadata sync', () => {
  const originalCreateObjectURL = globalThis.URL && globalThis.URL.createObjectURL
  const originalRevokeObjectURL = globalThis.URL && globalThis.URL.revokeObjectURL

  beforeAll(() => {
    if (!globalThis.URL) {
      globalThis.URL = {}
    }
    globalThis.URL.createObjectURL = vi.fn(() => 'blob:preview')
    globalThis.URL.revokeObjectURL = vi.fn()
  })

  beforeEach(() => {
    vi.clearAllMocks()
    useAppStore.setState((state) => ({
      ...state,
      templates: [JSON.parse(JSON.stringify(baseTemplate))],
    }))
  })

  afterEach(() => {
    useAppStore.setState((state) => ({ ...state, templates: [] }))
  })

  afterAll(() => {
    if (originalCreateObjectURL) {
      globalThis.URL.createObjectURL = originalCreateObjectURL
    } else {
      delete globalThis.URL.createObjectURL
    }
    if (originalRevokeObjectURL) {
      globalThis.URL.revokeObjectURL = originalRevokeObjectURL
    } else {
      delete globalThis.URL.revokeObjectURL
    }
  })

  it('omits last edit summary when no edits exist', async () => {
    getTemplateHtml.mockResolvedValue({ html: '<html></html>', metadata: null })
    renderEditor()
    await screen.findByLabelText(/Template HTML/i)
    expect(screen.queryByText(/Last edit:/i)).not.toBeInTheDocument()
  })

  it('updates store after manual save', async () => {
    const manualIso = '2025-11-18T14:32:00Z'
    getTemplateHtml.mockResolvedValue({ html: '<html></html>', metadata: null })
    editTemplateManual.mockResolvedValue({
      html: '<html>updated</html>',
      metadata: { lastEditType: 'manual', lastEditAt: manualIso },
    })

    renderEditor()
    await screen.findByLabelText(/Template HTML/i)

    const htmlField = screen.getByLabelText(/Template HTML/i)
    fireEvent.change(htmlField, { target: { value: '<html>changed</html>' } })

    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))

    await waitFor(() =>
      expect(
        screen.getByText((content) => content.includes('Last edit: Manual edit')),
      ).toBeInTheDocument(),
    )
    const template = useAppStore.getState().templates.find((t) => t.id === 'tpl-1')
    expect(template.generator.summary.lastEditType).toBe('manual')
  })

  it('updates store after AI edit', async () => {
    const aiIso = '2025-12-01T09:15:00Z'
    getTemplateHtml.mockResolvedValue({ html: '<html></html>', metadata: null })
    editTemplateAi.mockResolvedValue({
      html: '<html>ai</html>',
      metadata: { lastEditType: 'ai', lastEditAt: aiIso },
    })

    renderEditor()
    await screen.findByLabelText(/Template HTML/i)

    const [instructionsField] = screen.getAllByLabelText(/AI instructions/i)
    fireEvent.change(instructionsField, { target: { value: 'Revamp header' } })
    fireEvent.click(screen.getByRole('button', { name: /^apply ai$/i }))

    await waitFor(() =>
      expect(screen.getByText((content) => content.includes('Last edit: AI edit'))).toBeInTheDocument(),
    )
    const template = useAppStore.getState().templates.find((t) => t.id === 'tpl-1')
    expect(template.generator.summary.lastEditType).toBe('ai')
  })

  it('updates store after undo', async () => {
    const undoIso = '2025-12-05T08:00:00Z'
    getTemplateHtml.mockResolvedValue({ html: '<html></html>', metadata: null })
    undoTemplateEdit.mockResolvedValue({
      html: '<html>undo</html>',
      metadata: { lastEditType: 'undo', lastEditAt: undoIso },
    })

    renderEditor()
    await screen.findByLabelText(/Template HTML/i)

    fireEvent.click(screen.getByRole('button', { name: /^undo$/i }))

    await waitFor(() =>
      expect(screen.getByText((content) => content.includes('Last edit: Undo'))).toBeInTheDocument(),
    )
    const template = useAppStore.getState().templates.find((t) => t.id === 'tpl-1')
    expect(template.generator.summary.lastEditType).toBe('undo')
  })

  it('opens diff modal with before and after HTML', async () => {
    getTemplateHtml.mockResolvedValue({ html: '<div>Old HTML</div>', metadata: null })
    renderEditor()

    const htmlField = await screen.findByLabelText(/Template HTML/i)
    fireEvent.change(htmlField, { target: { value: '<div>New HTML</div>' } })

    fireEvent.click(screen.getByRole('button', { name: /View diff/i }))

    const dialog = await screen.findByRole('dialog')
    expect(within(dialog).getByText('HTML Changes')).toBeInTheDocument()
    expect(within(dialog).getByText((content) => content.includes('Old HTML'))).toBeInTheDocument()
    expect(within(dialog).getByText((content) => content.includes('New HTML'))).toBeInTheDocument()
  })
})
