/**
 * Custom hook: handles CSV and JSON export for DataTable
 */
import { useMemo, useCallback } from 'react'

export function useDataTableExport({ visibleColumns, sortedData, title }) {
  const exportColumns = useMemo(
    () => visibleColumns.filter((column) => column?.exportable !== false && column?.field),
    [visibleColumns],
  )

  const exportRows = useMemo(() => sortedData, [sortedData])

  const getExportValue = useCallback((row, column) => {
    if (typeof column.exportValue === 'function') {
      return column.exportValue(row[column.field], row)
    }
    if (typeof column.valueGetter === 'function') {
      return column.valueGetter(row)
    }
    return row[column.field]
  }, [])

  const formatCsvValue = useCallback((value) => {
    if (value === null || value === undefined) return ''
    if (value instanceof Date) return value.toISOString()
    const text = typeof value === 'string' ? value : JSON.stringify(value)
    const escaped = text.replace(/"/g, '""')
    if (/[",\n\r]/.test(escaped)) {
      return `"${escaped}"`
    }
    return escaped
  }, [])

  const buildExportFileName = useCallback((extension) => {
    const base = String(title || 'table-export').trim().toLowerCase()
    const safeBase = base.replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || 'table-export'
    return `${safeBase}.${extension}`
  }, [title])

  const downloadFile = useCallback((content, filename, type) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.rel = 'noopener'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }, [])

  const handleExportCsv = useCallback(() => {
    if (!exportColumns.length || !exportRows.length) return
    const headers = exportColumns.map((column) => column.headerName || column.field)
    const rows = exportRows.map((row) =>
      exportColumns.map((column) => formatCsvValue(getExportValue(row, column)))
    )
    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n')
    downloadFile(csv, buildExportFileName('csv'), 'text/csv;charset=utf-8;')
  }, [exportColumns, exportRows, formatCsvValue, getExportValue, downloadFile, buildExportFileName])

  const handleExportJson = useCallback(() => {
    if (!exportColumns.length || !exportRows.length) return
    const records = exportRows.map((row) => {
      const record = {}
      exportColumns.forEach((column) => {
        const key = column.field || column.headerName
        record[key] = getExportValue(row, column) ?? null
      })
      return record
    })
    const json = JSON.stringify(records, null, 2)
    downloadFile(json, buildExportFileName('json'), 'application/json;charset=utf-8;')
  }, [exportColumns, exportRows, getExportValue, downloadFile, buildExportFileName])

  return {
    exportColumns,
    exportRows,
    handleExportCsv,
    handleExportJson,
  }
}
