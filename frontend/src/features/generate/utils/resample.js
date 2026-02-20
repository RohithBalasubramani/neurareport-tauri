const MS_IN_MINUTE = 60 * 1000
const MS_IN_HOUR = 60 * MS_IN_MINUTE
const MS_IN_DAY = 24 * MS_IN_HOUR
const MS_IN_WEEK = 7 * MS_IN_DAY

export const DEFAULT_RESAMPLE_CONFIG = {
  dimension: 'time',
  dimensionKind: 'temporal',
  metric: 'rows',
  aggregation: 'sum',
  bucket: 'auto',
  range: null,
}

export const RESAMPLE_DIMENSION_OPTIONS = [
  { value: 'time', label: 'Time', kind: 'temporal', bucketable: true },
  { value: 'category', label: 'Category', kind: 'categorical', bucketable: false },
  { value: 'batch_index', label: 'Discovery order', kind: 'numeric', bucketable: true },
]

export const RESAMPLE_METRIC_OPTIONS = [
  { value: 'rows', label: 'Rows' },
  { value: 'rows_per_parent', label: 'Rows per parent' },
  { value: 'parent', label: 'Parent rows' },
]

export const RESAMPLE_AGGREGATION_OPTIONS = [
  { value: 'sum', label: 'Sum' },
  { value: 'avg', label: 'Average' },
  { value: 'max', label: 'Max' },
  { value: 'min', label: 'Min' },
]

export const RESAMPLE_BUCKET_OPTIONS = [
  { value: 'auto', label: 'Auto' },
  { value: 'minute', label: 'Minute' },
  { value: 'hour', label: 'Hour' },
  { value: 'day', label: 'Day' },
  { value: 'week', label: 'Week' },
  { value: 'month', label: 'Month' },
]

export const RESAMPLE_NUMERIC_BUCKET_OPTIONS = [
  { value: 'auto', label: 'Auto (10 buckets)' },
  { value: '5', label: '5 buckets' },
  { value: '10', label: '10 buckets' },
  { value: '20', label: '20 buckets' },
]

export const RESAMPLE_UNCATEGORIZED_LABEL = 'Uncategorized'

export const clampBrushRange = (range, maxIndex) => {
  if (!Array.isArray(range) || range.length !== 2 || maxIndex < 0) return null
  const start = Math.max(0, Math.min(maxIndex, Number(range[0]) || 0))
  const endRaw = Number(range[1])
  const end = Math.max(start, Math.min(maxIndex, Number.isFinite(endRaw) ? endRaw : maxIndex))
  return [start, end]
}

export const resolveTimeBucket = (metrics, requestedBucket) => {
  if (requestedBucket && requestedBucket !== 'auto') return requestedBucket
  const timestamps = (Array.isArray(metrics) ? metrics : [])
    .map((entry) => Date.parse(entry?.time ?? entry?.timestamp ?? ''))
    .filter((value) => !Number.isNaN(value))
  if (!timestamps.length) return 'day'
  const span = Math.max(...timestamps) - Math.min(...timestamps)
  if (span > 120 * MS_IN_DAY) return 'month'
  if (span > 35 * MS_IN_DAY) return 'week'
  if (span > 7 * MS_IN_DAY) return 'day'
  if (span > 6 * MS_IN_HOUR) return 'hour'
  return 'minute'
}

const truncateTimestampToBucket = (timestamp, bucket) => {
  if (timestamp == null) return null
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return null
  if (bucket === 'month') {
    return new Date(date.getFullYear(), date.getMonth(), 1).setHours(0, 0, 0, 0)
  }
  if (bucket === 'week') {
    const day = date.getDay()
    const diff = date.getDate() - day
    return new Date(date.getFullYear(), date.getMonth(), diff).setHours(0, 0, 0, 0)
  }
  if (bucket === 'day') {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate()).setHours(0, 0, 0, 0)
  }
  if (bucket === 'hour') {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours()).setMinutes(0, 0, 0)
  }
  return new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate(),
    date.getHours(),
    date.getMinutes(),
  ).setSeconds(0, 0)
}

const formatBucketLabel = (timestamp, bucket) => {
  if (timestamp == null) return ''
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return ''
  if (bucket === 'month') {
    return date.toLocaleString(undefined, { month: 'short', year: 'numeric' })
  }
  if (bucket === 'week' || bucket === 'day') {
    return date.toLocaleDateString()
  }
  if (bucket === 'hour') {
    return date.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
    })
  }
  return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}

export const collectIdsFromSeries = (series, range) => {
  const ids = new Set()
  if (!Array.isArray(series) || !Array.isArray(range)) return ids
  for (let idx = range[0]; idx <= range[1] && idx < series.length; idx += 1) {
    const bucket = series[idx]
    if (!bucket) continue
    const batchIds = Array.isArray(bucket.batchIds) ? bucket.batchIds : []
    batchIds.forEach((id) => ids.add(String(id)))
  }
  return ids
}

export const buildResampleComputation = (
  metrics,
  config = DEFAULT_RESAMPLE_CONFIG,
  numericBins = {},
  categoryGroups = {},
) => {
  const safeMetrics = Array.isArray(metrics) ? metrics : []
  const dimension = config?.dimension || DEFAULT_RESAMPLE_CONFIG.dimension
  let dimensionKind = config?.dimensionKind || DEFAULT_RESAMPLE_CONFIG.dimensionKind
  if (!config?.dimensionKind) {
    if (dimension === 'time') {
      dimensionKind = 'temporal'
    } else if (dimension === 'category') {
      dimensionKind = 'categorical'
    } else {
      dimensionKind = 'numeric'
    }
  }
  const metricKey = config?.metric || DEFAULT_RESAMPLE_CONFIG.metric
  const aggregation = config?.aggregation || DEFAULT_RESAMPLE_CONFIG.aggregation
  const bucketSelection = config?.bucket || DEFAULT_RESAMPLE_CONFIG.bucket
  const resolvedBucket =
    dimensionKind === 'temporal' || dimension === 'time'
      ? resolveTimeBucket(safeMetrics, bucketSelection)
      : 'none'
  const groupsMap = new Map()

  if (dimensionKind === 'categorical' && Array.isArray(categoryGroups?.[dimension])) {
    const precomputed = categoryGroups[dimension]
    const series = precomputed
      .map((entry, idx) => {
        const key = entry?.key ?? entry?.label ?? `cat:${idx}`
        const label = entry?.label ?? key
        const value = Number(entry?.value) || 0
        const batchIds = Array.isArray(entry?.batch_ids) ? entry.batch_ids.map((id) => String(id)) : []
        const sortValue = typeof entry?.sortValue === 'number' ? entry.sortValue : label.toLowerCase()
        return { key, label, value, sortValue, batchIds }
      })
      .filter((entry) => entry.key)
    series.sort((a, b) => {
      if (typeof a.sortValue === 'number' && typeof b.sortValue === 'number') return a.sortValue - b.sortValue
      return String(a.sortValue).localeCompare(String(b.sortValue))
    })
    const maxIndex = series.length - 1
    const hasUserRange = Array.isArray(config?.range) && config.range.length === 2
    const clampedRange = clampBrushRange(hasUserRange ? config.range : [0, maxIndex], maxIndex) ?? [0, maxIndex]
    const coversAll = clampedRange[0] === 0 && clampedRange[1] === maxIndex
    const filterActive = hasUserRange && !coversAll
    const allowedIds = filterActive ? collectIdsFromSeries(series, clampedRange) : null
    return {
      series,
      resolvedBucket: 'none',
      displayRange: clampedRange,
      configRange: filterActive ? clampedRange : null,
      allowedIds,
      filterActive,
    }
  }

  safeMetrics.forEach((entry, idx) => {
    const batchIndexRaw = entry?.batch_index
    const batchIndex = Number.isFinite(Number(batchIndexRaw)) ? Number(batchIndexRaw) : idx + 1
    const batchId = entry?.batch_id ?? entry?.batchId ?? entry?.id ?? batchIndex
    if (batchId == null) return
    const metricValue = Number(entry?.[metricKey]) || 0
    let groupKey = ''
    let sortValue = 0
    let label = ''
    if (dimensionKind === 'temporal' || dimension === 'time') {
      const timestamp = Date.parse(entry?.time ?? entry?.timestamp ?? '')
      if (Number.isNaN(timestamp)) return
      const truncated = truncateTimestampToBucket(timestamp, resolvedBucket)
      if (truncated == null) return
      groupKey = `${resolvedBucket}:${truncated}`
      sortValue = truncated
      label = formatBucketLabel(truncated, resolvedBucket)
    } else if (dimensionKind === 'categorical' || dimension === 'category') {
      const category = entry?.category != null && String(entry.category).trim().length
        ? String(entry.category)
        : RESAMPLE_UNCATEGORIZED_LABEL
      groupKey = `cat:${category}`
      sortValue = category.toLowerCase()
      label = category
    } else if (dimensionKind === 'numeric') {
      const value = Number(entry?.[dimension])
      if (!Number.isFinite(value)) return
      const bucketCount = bucketSelection && bucketSelection !== 'auto' ? Number(bucketSelection) || 10 : 10
      // Build bucket edges lazily based on min/max
      const existing = groupsMap.get('__numeric_meta__') || { key: '__numeric_meta__', min: value, max: value }
      existing.min = Math.min(existing.min, value)
      existing.max = Math.max(existing.max, value)
      existing.bucketCount = bucketCount
      groupsMap.set('__numeric_meta__', existing)
      groupKey = `num:${value}`
      sortValue = value
      label = value.toString()
    } else {
      groupKey = `idx:${batchIndex}`
      sortValue = batchIndex
      label = `Batch ${batchIndex}`
    }
    const existing = groupsMap.get(groupKey) || {
      key: groupKey,
      label,
      sortValue,
      sum: 0,
      count: 0,
      min: Number.POSITIVE_INFINITY,
      max: Number.NEGATIVE_INFINITY,
      batchIds: new Set(),
    }
    existing.sum += metricValue
    existing.count += 1
    existing.min = Math.min(existing.min, metricValue)
    existing.max = Math.max(existing.max, metricValue)
    existing.batchIds.add(String(batchId))
    groupsMap.set(groupKey, existing)
  })

  const series = Array.from(groupsMap.values())
    .map((entry) => {
      if (entry.key === '__numeric_meta__' || !entry.batchIds) {
        return null
      }
      let value = entry.sum
      if (aggregation === 'avg') {
        value = entry.count ? entry.sum / entry.count : 0
      } else if (aggregation === 'max') {
        value = entry.max === Number.NEGATIVE_INFINITY ? 0 : entry.max
      } else if (aggregation === 'min') {
        value = entry.min === Number.POSITIVE_INFINITY ? 0 : entry.min
      }
      return {
        key: entry.key,
        label: entry.label,
        value,
        sortValue: entry.sortValue,
        batchIds: Array.from(entry.batchIds),
      }
    })
    .sort((a, b) => {
      if (!a || !b) return 0
      if (typeof a.sortValue === 'number' && typeof b.sortValue === 'number') {
        return a.sortValue - b.sortValue
      }
      return String(a.sortValue).localeCompare(String(b.sortValue))
    })
    .filter(Boolean)

  if (dimensionKind === 'numeric') {
    const binsForDimension = Array.isArray(numericBins?.[dimension]) ? numericBins[dimension] : null
    const meta = groupsMap.get('__numeric_meta__') || {}
    const bucketCount = meta?.bucketCount || 10
    const requestedBinCount = bucketSelection && bucketSelection !== 'auto' ? Number(bucketSelection) || null : null
    const numericEntries = safeMetrics
      .map((entry, idxMetric) => ({
        value: Number(entry?.[dimension]),
        batchId: entry?.batch_id ?? entry?.id ?? idxMetric + 1,
      }))
      .filter((item) => Number.isFinite(item.value))
    const canUseBackendBins =
      binsForDimension &&
      metricKey === dimension &&
      (!requestedBinCount || requestedBinCount === binsForDimension.length)
    if (canUseBackendBins) {
      const aggregated = binsForDimension.map((bucket, idx) => {
        const count = Number(bucket?.count) || 0
        const sum = Number(bucket?.sum) || 0
        const min = Number.isFinite(bucket?.min) ? Number(bucket.min) : 0
        const max = Number.isFinite(bucket?.max) ? Number(bucket.max) : 0
        let value = sum
        if (aggregation === 'avg') {
          value = count ? sum / count : 0
        } else if (aggregation === 'count') {
          value = count
        } else if (aggregation === 'max') {
          value = max
        } else if (aggregation === 'min') {
          value = min
        }
        const startRaw = Number(bucket?.start)
        const endRaw = Number(bucket?.end)
        const start = Number.isFinite(startRaw) ? startRaw : idx
        const end = Number.isFinite(endRaw) ? endRaw : idx + 1
        return {
          key: `bin:${idx}`,
          label: `${start} - ${end}`,
          value,
          sortValue: start,
          batchIds: Array.isArray(bucket?.batch_ids) ? bucket.batch_ids.map((id) => String(id)) : [],
        }
      })
      aggregated.sort((a, b) => a.sortValue - b.sortValue)
      const maxIndex = aggregated.length - 1
      const hasUserRange = Array.isArray(config?.range) && config.range.length === 2
      const clampedRange =
        clampBrushRange(hasUserRange ? config.range : [0, maxIndex], maxIndex) ?? [0, maxIndex]
      const coversAll = clampedRange[0] === 0 && clampedRange[1] === maxIndex
      const filterActive = hasUserRange && !coversAll
      const allowedIds = filterActive ? collectIdsFromSeries(aggregated, clampedRange) : null
      return {
        series: aggregated,
        resolvedBucket: bucketSelection || 'auto',
        displayRange: clampedRange,
        configRange: filterActive ? clampedRange : null,
        allowedIds,
        filterActive,
      }
    }

    if (numericEntries.length) {
      const min = meta?.min ?? Math.min(...numericEntries.map((e) => e.value))
      const max = meta?.max ?? Math.max(...numericEntries.map((e) => e.value))
      const step = bucketCount > 0 ? (max - min) / bucketCount : 0
      const buckets = []
      for (let i = 0; i < bucketCount; i += 1) {
        const start = min + step * i
        const end = i === bucketCount - 1 ? max : min + step * (i + 1)
        buckets.push({
          key: `bucket:${i}`,
          label: `${start.toFixed(2)} - ${end.toFixed(2)}`,
          sortValue: start,
          sum: 0,
          count: 0,
          min: Number.POSITIVE_INFINITY,
          max: Number.NEGATIVE_INFINITY,
          batchIds: new Set(),
        })
      }
      numericEntries.forEach(({ value, batchId }) => {
        let target = 0
        if (step > 0) {
          const pos = Math.floor((value - min) / step)
          target = Math.min(bucketCount - 1, Math.max(0, pos))
        }
        const bucket = buckets[target]
        bucket.sum += value
        bucket.count += 1
        bucket.min = Math.min(bucket.min, value)
        bucket.max = Math.max(bucket.max, value)
        if (batchId != null) bucket.batchIds.add(String(batchId))
      })
      const aggregated = buckets.map((bucket) => ({
        key: bucket.key,
        label: bucket.label,
        value:
          aggregation === 'avg'
            ? bucket.count
              ? bucket.sum / bucket.count
              : 0
            : aggregation === 'max'
              ? bucket.max === Number.NEGATIVE_INFINITY
                ? 0
                : bucket.max
              : aggregation === 'min'
                ? bucket.min === Number.POSITIVE_INFINITY
                  ? 0
                  : bucket.min
                : aggregation === 'count'
                  ? bucket.count
                  : bucket.sum,
        sortValue: bucket.sortValue,
        batchIds: Array.from(bucket.batchIds),
      }))
      aggregated.sort((a, b) => a.sortValue - b.sortValue)
      const maxIndex = aggregated.length - 1
      const hasUserRange = Array.isArray(config?.range) && config.range.length === 2
      const clampedRange =
        clampBrushRange(hasUserRange ? config.range : [0, maxIndex], maxIndex) ?? [0, maxIndex]
      const coversAll = clampedRange[0] === 0 && clampedRange[1] === maxIndex
      const filterActive = hasUserRange && !coversAll
      const allowedIds = filterActive ? collectIdsFromSeries(aggregated, clampedRange) : null
      return {
        series: aggregated,
        resolvedBucket: bucketSelection || 'auto',
        displayRange: clampedRange,
        configRange: filterActive ? clampedRange : null,
        allowedIds,
        filterActive,
      }
    }
  }

  if (!series.length) {
    return {
      series,
      resolvedBucket,
      displayRange: null,
      configRange: null,
      allowedIds: null,
      filterActive: false,
    }
  }

  const maxIndex = series.length - 1
  const hasUserRange = Array.isArray(config?.range) && config.range.length === 2
  const clampedRange = clampBrushRange(hasUserRange ? config.range : [0, maxIndex], maxIndex) ?? [0, maxIndex]
  const coversAll = clampedRange[0] === 0 && clampedRange[1] === maxIndex
  const filterActive = hasUserRange && !coversAll
  const allowedIds = filterActive ? collectIdsFromSeries(series, clampedRange) : null

  return {
    series,
    resolvedBucket,
    displayRange: clampedRange,
    configRange: filterActive ? clampedRange : null,
    allowedIds,
    filterActive,
  }
}
