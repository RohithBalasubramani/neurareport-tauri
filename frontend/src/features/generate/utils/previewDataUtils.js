export function resolveChartPreviewDataset(activeData, sampleData) {
  const hasActive = Array.isArray(activeData) && activeData.length > 0
  if (hasActive) {
    return {
      data: activeData,
      usingSampleData: false,
    }
  }
  const hasSample = Array.isArray(sampleData) && sampleData.length > 0
  if (hasSample) {
    return {
      data: sampleData,
      usingSampleData: true,
    }
  }
  return {
    data: [],
    usingSampleData: false,
  }
}
