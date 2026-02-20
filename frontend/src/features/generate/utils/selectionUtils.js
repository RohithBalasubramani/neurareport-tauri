export const normalizeBatchId = (batch, index) => {
  if (batch && batch.id != null) {
    return String(batch.id)
  }
  return String(index)
}

export const getScopedBatchEntries = (batches, templateId, activeBatchFilter, options = {}) => {
  const { requireSelected = false } = options
  if (!Array.isArray(batches)) return []
  return batches
    .map((batch, index) => {
      if (!batch) return null
      if (requireSelected && !batch.selected) return null
      const batchId = normalizeBatchId(batch, index)
      if (activeBatchFilter && templateId) {
        const allowed = activeBatchFilter[templateId]
        if (allowed && allowed.size && !allowed.has(batchId)) {
          return null
        }
      }
      return { batch, index, batchId }
    })
    .filter(Boolean)
}

