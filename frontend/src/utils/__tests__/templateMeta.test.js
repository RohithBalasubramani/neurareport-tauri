import { describe, expect, it } from 'vitest'

import { buildLastEditInfo, formatLastEditTimestamp } from '../templateMeta'

describe('formatLastEditTimestamp', () => {
  it('formats ISO strings into a short timestamp', () => {
    const result = formatLastEditTimestamp('2025-11-18T14:32:00Z')
    expect(result).not.toBeNull()
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/)
  })

  it('returns null for invalid or empty values', () => {
    expect(formatLastEditTimestamp('not-a-date')).toBeNull()
    expect(formatLastEditTimestamp('')).toBeNull()
    expect(formatLastEditTimestamp(null)).toBeNull()
  })
})

describe('buildLastEditInfo', () => {
  const iso = '2025-11-18T14:32:00Z'

  it('builds info for AI edits', () => {
    const info = buildLastEditInfo({ lastEditType: 'ai', lastEditAt: iso })
    expect(info.type).toBe('ai')
    expect(info.chipLabel).toContain('AI edit')
    expect(info.timestampLabel).toBe(formatLastEditTimestamp(iso))
    expect(info.color).toBe('secondary')
    expect(info.variant).toBe('filled')
  })

  it('builds info for manual edits', () => {
    const info = buildLastEditInfo({ lastEditType: 'manual', lastEditAt: iso })
    expect(info.type).toBe('manual')
    expect(info.chipLabel).toContain('Manual edit')
    expect(info.color).toBe('primary')
    expect(info.variant).toBe('filled')
  })

  it('builds info for undo entries', () => {
    const info = buildLastEditInfo({ lastEditType: 'undo', lastEditAt: iso })
    expect(info.type).toBe('undo')
    expect(info.chipLabel).toContain('Undo')
    expect(info.color).toBe('warning')
    expect(info.variant).toBe('outlined')
  })

  it('returns null when no type or timestamp available', () => {
    expect(buildLastEditInfo({})).toBeNull()
    expect(buildLastEditInfo(undefined)).toBeNull()
  })
})
