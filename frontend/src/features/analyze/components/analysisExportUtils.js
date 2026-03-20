export const exportCSV = (raw_data, document_name) => {
  if (!raw_data || raw_data.length === 0) return

  const headers = Object.keys(raw_data[0])
  const csvRows = [
    headers.join(','),
    ...raw_data.map((row) =>
      headers.map((h) => {
        const val = row[h]
        if (val === null || val === undefined) return ''
        const str = String(val)
        return str.includes(',') || str.includes('"') ? `"${str.replace(/"/g, '""')}"` : str
      }).join(',')
    ),
  ]
  const csvContent = csvRows.join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${document_name || 'analysis'}_data.csv`
  link.click()
  URL.revokeObjectURL(url)
}

export const exportJSON = (raw_data, document_name) => {
  if (!raw_data || raw_data.length === 0) return

  const jsonContent = JSON.stringify(raw_data, null, 2)
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${document_name || 'analysis'}_data.json`
  link.click()
  URL.revokeObjectURL(url)
}
