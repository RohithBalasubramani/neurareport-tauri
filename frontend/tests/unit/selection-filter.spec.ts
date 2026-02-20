import { test, expect } from '@playwright/test'
import { getScopedBatchEntries, normalizeBatchId } from '../../src/features/generate/utils/selectionUtils.js'

const templateId = 'tpl-1'
const baseBatches = [
  { id: 'alpha', rows: 120, selected: true, parent: 2 },
  { id: 'beta', rows: 40, selected: true, parent: 1 },
  { rows: 15, selected: true, parent: 1 },
  { id: 'gamma', rows: 70, selected: false, parent: 1 },
]

test.describe('selection intersection helpers', () => {
  test('normalizeBatchId falls back to positional value', () => {
    expect(normalizeBatchId({ id: 42 }, 3)).toBe('42')
    expect(normalizeBatchId({ id: 'batch-7' }, 1)).toBe('batch-7')
    expect(normalizeBatchId({ selected: true }, 5)).toBe('5')
    expect(normalizeBatchId(null, 2)).toBe('2')
  })

  test('getScopedBatchEntries respects manual selection and active filter', () => {
    const noFilterEntries = getScopedBatchEntries(baseBatches, templateId, null, { requireSelected: true })
    expect(noFilterEntries.map((entry) => entry.batchId)).toEqual(['alpha', 'beta', '2'])

    const activeFilter = { [templateId]: new Set(['beta']) }
    const filteredEntries = getScopedBatchEntries(baseBatches, templateId, activeFilter, { requireSelected: true })
    expect(filteredEntries.map((entry) => entry.batchId)).toEqual(['beta'])

    const includeFallbackId = { [templateId]: new Set(['2']) }
    const fallbackEntries = getScopedBatchEntries(baseBatches, templateId, includeFallbackId, { requireSelected: true })
    expect(fallbackEntries.map((entry) => entry.batchId)).toEqual(['2'])

    const crossTemplateFilter = { other: new Set(['alpha', 'beta']) }
    const unaffected = getScopedBatchEntries(baseBatches, templateId, crossTemplateFilter, { requireSelected: true })
    expect(unaffected.map((entry) => entry.batchId)).toEqual(['alpha', 'beta', '2'])
  })

  test('helpers can drive chart + run metrics parity', () => {
    const results = { [templateId]: { name: 'Flow Template', batches: baseBatches } }

    const scopedAll = getScopedBatchEntries(results[templateId].batches, templateId, null)
    const totals = scopedAll.reduce(
      (acc, { batch }) => {
        const rows = batch.rows || 0
        acc.totalRows += rows
        acc.totalBatches += 1
        if (batch.selected) {
          acc.selectedRows += rows
          acc.selectedBatches += 1
        }
        return acc
      },
      { totalRows: 0, selectedRows: 0, totalBatches: 0, selectedBatches: 0 },
    )
    expect(totals).toEqual({
      totalRows: 245,
      selectedRows: 175,
      totalBatches: 4,
      selectedBatches: 3,
    })
    const runIds = getScopedBatchEntries(results[templateId].batches, templateId, null, { requireSelected: true })
      .map(({ batch }) => batch.id)
    expect(runIds).toEqual(['alpha', 'beta', undefined])
    expect(runIds.some((id) => id != null)).toBe(true)

    const scopedFilter = { [templateId]: new Set(['alpha', '2']) }
    const filteredTotals = getScopedBatchEntries(results[templateId].batches, templateId, scopedFilter).reduce(
      (acc, { batch }) => {
        const rows = batch.rows || 0
        acc.totalRows += rows
        acc.totalBatches += 1
        if (batch.selected) {
          acc.selectedRows += rows
          acc.selectedBatches += 1
        }
        return acc
      },
      { totalRows: 0, selectedRows: 0, totalBatches: 0, selectedBatches: 0 },
    )
    expect(filteredTotals).toEqual({
      totalRows: 135,
      selectedRows: 135,
      totalBatches: 2,
      selectedBatches: 2,
    })
    const filteredRunIds = getScopedBatchEntries(results[templateId].batches, templateId, scopedFilter, {
      requireSelected: true,
    }).map(({ batch }) => batch.id)
    expect(filteredRunIds).toEqual(['alpha', undefined])
    expect(filteredRunIds.every((id) => id === 'alpha' || id === undefined)).toBe(true)
  })
})

