import { useState, useCallback, useEffect } from 'react'

const formatDateForInput = (date) => date.toISOString().split('T')[0]

const getDatePresets = () => {
  const today = new Date()
  const startOfWeek = new Date(today)
  startOfWeek.setDate(today.getDate() - today.getDay())
  const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
  const startOfLastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1)
  const endOfLastMonth = new Date(today.getFullYear(), today.getMonth(), 0)

  return {
    today: {
      label: 'Today',
      start: formatDateForInput(today),
      end: formatDateForInput(today),
    },
    thisWeek: {
      label: 'This Week',
      start: formatDateForInput(startOfWeek),
      end: formatDateForInput(today),
    },
    thisMonth: {
      label: 'This Month',
      start: formatDateForInput(startOfMonth),
      end: formatDateForInput(today),
    },
    lastMonth: {
      label: 'Last Month',
      start: formatDateForInput(startOfLastMonth),
      end: formatDateForInput(endOfLastMonth),
    },
  }
}

/** Compose date+time for the API. Returns "YYYY-MM-DD HH:MM" when time is set, "YYYY-MM-DD" otherwise. */
export const composeDateTimeString = (dateStr, timeStr) => {
  if (!dateStr) return ''
  if (!timeStr) return dateStr
  return `${dateStr} ${timeStr}`
}

export { getDatePresets }

export default function useReportDateRange() {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [datePreset, setDatePreset] = useState('thisMonth')

  const handleDatePreset = useCallback((presetKey) => {
    setDatePreset(presetKey)
    if (presetKey !== 'custom') {
      const presets = getDatePresets()
      const preset = presets[presetKey]
      if (preset) {
        setStartDate(preset.start)
        setEndDate(preset.end)
        setStartTime('')
        setEndTime('')
      }
    }
  }, [])

  // Initialize dates on first render
  useEffect(() => {
    if (!startDate && !endDate && datePreset !== 'custom') {
      const presets = getDatePresets()
      const preset = presets[datePreset]
      if (preset) {
        setStartDate(preset.start)
        setEndDate(preset.end)
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return {
    startDate,
    setStartDate,
    endDate,
    setEndDate,
    startTime,
    setStartTime,
    endTime,
    setEndTime,
    datePreset,
    setDatePreset,
    handleDatePreset,
  }
}
