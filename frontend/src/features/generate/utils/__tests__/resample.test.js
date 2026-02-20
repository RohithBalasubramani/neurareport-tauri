import { describe, it, expect } from 'vitest'

import {
  buildResampleComputation,
  RESAMPLE_UNCATEGORIZED_LABEL,
  resolveTimeBucket,
} from '../resample'

describe('resolveTimeBucket', () => {
  it('returns requested bucket when provided', () => {
    const metrics = [
      { time: '2024-01-01T00:00:00Z' },
      { time: '2024-01-08T00:00:00Z' },
    ]
    expect(resolveTimeBucket(metrics, 'week')).toBe('week')
  })

  it('infers a coarse bucket for wide time ranges', () => {
    const metrics = [
      { time: '2024-01-01T00:00:00Z' },
      { time: '2024-06-15T00:00:00Z' },
    ]
    expect(resolveTimeBucket(metrics, 'auto')).toBe('month')
  })

  it('falls back to finer buckets for short ranges', () => {
    const hourlyMetrics = [
      { time: '2024-01-01T00:00:00Z' },
      { time: '2024-01-01T12:00:00Z' },
    ]
    expect(resolveTimeBucket(hourlyMetrics, 'auto')).toBe('hour')

    const minuteMetrics = [
      { time: '2024-01-01T00:00:00Z' },
      { time: '2024-01-01T00:05:00Z' },
    ]
    expect(resolveTimeBucket(minuteMetrics, 'auto')).toBe('minute')
  })
})

describe('buildResampleComputation', () => {
  it('retains category labels and fills uncategorized buckets', () => {
    const metrics = [
      { batch_index: 1, batch_id: 'b1', rows: 10, category: 'North' },
      { batch_index: 2, batch_id: 'b2', rows: 5, category: '' },
      { batch_index: 3, batch_id: 'b3', rows: 3 },
    ]

    const result = buildResampleComputation(metrics, {
      dimension: 'category',
      metric: 'rows',
      aggregation: 'sum',
      bucket: 'auto',
      range: null,
    })

    const labels = result.series.map((entry) => entry.label)
    expect(labels).toContain('North')
    expect(labels).toContain(RESAMPLE_UNCATEGORIZED_LABEL)
    const northBucket = result.series.find((entry) => entry.label === 'North')
    expect(northBucket?.value).toBe(10)
  })

  it('uses backend numeric bins when provided', () => {
    const metrics = [
      { batch_index: 1, batch_id: 'b1', rows: 2 },
      { batch_index: 2, batch_id: 'b2', rows: 4 },
    ]
    const bins = {
      rows: [
        {
          bucket_index: 0,
          start: 0,
          end: 5,
          count: 2,
          sum: 6,
          min: 2,
          max: 4,
          batch_ids: ['b1', 'b2'],
        },
      ],
    }

    const result = buildResampleComputation(
      metrics,
      {
        dimension: 'rows',
        dimensionKind: 'numeric',
        metric: 'rows',
        aggregation: 'sum',
        bucket: 'auto',
        range: null,
      },
      bins,
    )

    expect(result.series).toHaveLength(1)
    expect(result.series[0].value).toBe(6)
    expect(result.series[0].batchIds).toEqual(['b1', 'b2'])
  })

  it('uses precomputed category groups with range filtering', () => {
    const categoryGroups = {
      category: [
        { key: 'A', label: 'Alpha', value: 10, batch_ids: ['1', '2'] },
        { key: 'B', label: 'Beta', value: 5, batch_ids: ['3'] },
        { key: 'C', label: 'Gamma', value: 2, batch_ids: ['4'] },
      ],
    }
    const result = buildResampleComputation(
      [],
      {
        dimension: 'category',
        dimensionKind: 'categorical',
        metric: 'rows',
        aggregation: 'sum',
        bucket: 'auto',
        range: [0, 1],
      },
      {},
      categoryGroups,
    )
    expect(result.series).toHaveLength(3)
    expect(result.series[0].label).toBe('Alpha')
    expect(result.series[1].label).toBe('Beta')
    expect(result.filterActive).toBe(true)
    expect(result.allowedIds).toBeInstanceOf(Set)
    expect(result.allowedIds.has('1')).toBe(true)
    expect(result.allowedIds.has('3')).toBe(true)
    expect(result.allowedIds.has('4')).toBe(false)
  })
})
