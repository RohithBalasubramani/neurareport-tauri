import { describe, expect, it, vi } from 'vitest'

vi.mock('../client', () => ({
  sleep: () => Promise.resolve(),
}))

import { editTemplateManual, editTemplateAi, undoTemplateEdit } from '../mock'

describe('mock template edit helpers', () => {
  it('returns metadata for manual edits', async () => {
    const result = await editTemplateManual('tpl-1', '<html></html>')
    expect(result.metadata.lastEditType).toBe('manual')
    expect(result.metadata.lastEditAt).toBeTruthy()
  })

  it('returns metadata for AI edits', async () => {
    const result = await editTemplateAi('tpl-1', 'Add colors', '<html></html>')
    expect(result.metadata.lastEditType).toBe('ai')
    expect(result.metadata.lastEditAt).toBeTruthy()
    expect(result.summary).toBeDefined()
  })

  it('returns metadata for undo operations', async () => {
    const result = await undoTemplateEdit('tpl-1')
    expect(result.metadata.lastEditType).toBe('undo')
    expect(result.metadata.lastEditAt).toBeTruthy()
  })
})

