import assert from 'node:assert/strict'
import { test } from 'node:test'

import { resolveChartPreviewDataset } from '../../src/features/generate/utils/previewDataUtils.js'

test('resolveChartPreviewDataset prefers active discovery data', () => {
  const active = [{ batch_index: 1 }]
  const sample = [{ batch_index: 99 }]
  const result = resolveChartPreviewDataset(active, sample)
  assert.deepEqual(result.data, active)
  assert.equal(result.usingSampleData, false)
})

test('resolveChartPreviewDataset falls back to sample data when discovery data missing', () => {
  const sample = [{ batch_index: 42 }]
  const result = resolveChartPreviewDataset([], sample)
  assert.deepEqual(result.data, sample)
  assert.equal(result.usingSampleData, true)
})

test('resolveChartPreviewDataset returns empty array when no data is available', () => {
  const result = resolveChartPreviewDataset([], [])
  assert.deepEqual(result.data, [])
  assert.equal(result.usingSampleData, false)
})
