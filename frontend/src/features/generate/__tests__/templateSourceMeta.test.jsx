import { describe, it, expect } from 'vitest'

import { getSourceMeta } from '@/features/generate/utils/templateSourceMeta.js'

describe('getSourceMeta', () => {
  it('returns company meta for company source', () => {
    const meta = getSourceMeta('company')
    expect(meta.label).toMatch(/company/i)
    expect(meta.color).toBe('default')
    expect(meta.variant).toBe('outlined')
    expect(meta.isStarter).toBe(false)
  })

  it('returns starter meta for starter source', () => {
    const meta = getSourceMeta('starter')
    expect(meta.label).toMatch(/starter/i)
    expect(meta.color).toBe('secondary')
    expect(meta.variant).toBe('outlined')
    expect(meta.isStarter).toBe(true)
  })

  it('defaults to company meta for unknown sources', () => {
    const meta = getSourceMeta(undefined)
    expect(meta.label).toMatch(/company/i)
    expect(meta.isStarter).toBe(false)
  })
})
