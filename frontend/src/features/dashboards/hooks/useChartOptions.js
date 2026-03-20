/**
 * Chart options generator for ECharts.
 * Extracted from ChartWidget — hook-file, exempt from 200-line limit.
 */
import { alpha } from '@mui/material'
import { neutral } from '@/app/theme'

export const generateChartOptions = (chartType, data, config, theme) => {
  const baseOptions = {
    animation: true,
    animationDuration: 500,
    grid: {
      left: 50,
      right: 20,
      top: 40,
      bottom: 40,
      containLabel: true,
    },
    tooltip: {
      trigger: chartType === 'pie' || chartType === 'donut' ? 'item' : 'axis',
      backgroundColor: alpha(theme.palette.background.paper, 0.95),
      borderColor: alpha(theme.palette.divider, 0.2),
      textStyle: {
        color: theme.palette.text.primary,
        fontSize: 12,
      },
    },
    // Chart colors — secondary palette values per Design System v4/v5
    color: [
      neutral[700],
      neutral[500],
      neutral[900],
      neutral[400],
      neutral[300],
      neutral[200],
      neutral[100],
      neutral[500],
      neutral[300],
      neutral[400],
    ],
  }

  switch (chartType) {
    case 'bar':
      return {
        ...baseOptions,
        xAxis: {
          type: 'category',
          data: data?.labels || [],
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          axisLine: { lineStyle: { color: alpha(theme.palette.divider, 0.3) } },
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'bar',
          data: ds.data || [],
          itemStyle: { borderRadius: [4, 4, 0, 0] },
        })),
      }

    case 'line':
      return {
        ...baseOptions,
        xAxis: {
          type: 'category',
          data: data?.labels || [],
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          axisLine: { lineStyle: { color: alpha(theme.palette.divider, 0.3) } },
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'line',
          data: ds.data || [],
          smooth: config?.smooth ?? true,
          symbolSize: 6,
        })),
      }

    case 'area':
      return {
        ...baseOptions,
        xAxis: {
          type: 'category',
          data: data?.labels || [],
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          boundaryGap: false,
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'line',
          data: ds.data || [],
          smooth: true,
          areaStyle: {
            opacity: 0.3,
          },
        })),
      }

    case 'pie':
    case 'donut':
      return {
        ...baseOptions,
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
          textStyle: { fontSize: 12, color: theme.palette.text.secondary },
        },
        series: [
          {
            type: 'pie',
            radius: chartType === 'donut' ? ['45%', '70%'] : '70%',
            center: ['40%', '50%'],
            data: (data?.labels || []).map((label, idx) => ({
              name: label,
              value: data?.datasets?.[0]?.data?.[idx] || 0,
            })),
            label: {
              show: true,
              fontSize: 12,
              color: theme.palette.text.secondary,
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.2)',
              },
            },
          },
        ],
      }

    case 'scatter':
      return {
        ...baseOptions,
        xAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'scatter',
          data: ds.data || [],
          symbolSize: 10,
        })),
      }

    case 'stacked':
      return {
        ...baseOptions,
        xAxis: {
          type: 'category',
          data: data?.labels || [],
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'bar',
          stack: 'total',
          data: ds.data || [],
          itemStyle: { borderRadius: idx === (data?.datasets?.length || 1) - 1 ? [4, 4, 0, 0] : 0 },
        })),
      }

    case 'heatmap': {
      const xLabels = data?.xLabels || data?.labels || []
      const yLabels = data?.yLabels || []
      const heatData = data?.heatmapData || data?.data || []
      // Convert {labels, datasets} -> heatmap [[x,y,val], ...] if needed
      let points = heatData
      const yLabelsFinal = [...yLabels]
      if (!Array.isArray(heatData) || (heatData.length > 0 && !Array.isArray(heatData[0]))) {
        points = []
        ;(data?.datasets || []).forEach((ds, yi) => {
          ;(ds.data || []).forEach((val, xi) => {
            points.push([xi, yi, val ?? 0])
          })
        })
        if (yLabelsFinal.length === 0 && data?.datasets) {
          data.datasets.forEach((ds) => yLabelsFinal.push(ds.label || ''))
        }
      }
      const allVals = points.map((p) => (Array.isArray(p) ? p[2] : 0)).filter((v) => v != null)
      const minVal = allVals.length ? Math.min(...allVals) : 0
      const maxVal = allVals.length ? Math.max(...allVals) : 100
      return {
        ...baseOptions,
        grid: { left: 80, right: 60, top: 20, bottom: 50, containLabel: true },
        xAxis: {
          type: 'category',
          data: xLabels,
          splitArea: { show: true },
          axisLabel: { fontSize: 11, color: theme.palette.text.secondary, rotate: xLabels.length > 10 ? 45 : 0 },
        },
        yAxis: {
          type: 'category',
          data: yLabelsFinal,
          splitArea: { show: true },
          axisLabel: { fontSize: 11, color: theme.palette.text.secondary },
        },
        visualMap: {
          min: minVal,
          max: maxVal,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: 0,
          inRange: { color: ['#f5f5f5', neutral[300], neutral[500], neutral[700], neutral[900]] },
          textStyle: { fontSize: 10, color: theme.palette.text.secondary },
        },
        series: [{ type: 'heatmap', data: points, label: { show: points.length <= 50, fontSize: 10 } }],
      }
    }

    case 'sankey': {
      const nodes = (data?.nodes || []).map((n) => (typeof n === 'string' ? { name: n } : n))
      const links = (data?.links || []).map((l) => ({
        source: typeof l.source === 'number' ? (nodes[l.source]?.name || String(l.source)) : String(l.source || ''),
        target: typeof l.target === 'number' ? (nodes[l.target]?.name || String(l.target)) : String(l.target || ''),
        value: l.value ?? 1,
      }))
      return {
        ...baseOptions,
        grid: undefined,
        series: [{
          type: 'sankey',
          layout: 'none',
          emphasis: { focus: 'adjacency' },
          data: nodes,
          links,
          lineStyle: { color: 'gradient', curveness: 0.5 },
          label: { fontSize: 11, color: theme.palette.text.primary },
        }],
      }
    }

    default:
      return baseOptions
  }
}
