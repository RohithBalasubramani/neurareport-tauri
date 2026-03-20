import { ResponsiveContainer } from 'recharts'
import { Box, IconButton, Stack, Typography, Chip, CircularProgress, Tooltip as MuiTooltip, alpha } from '@mui/material'
import { neutral } from '@/app/theme'
import ZoomOutMapIcon from '@mui/icons-material/ZoomOutMap'
import DownloadIcon from '@mui/icons-material/Download'
import { useZoomableChart } from '../hooks/useZoomableChart'
import ChartRenderer from './ChartRenderer'

export default function ZoomableChart({
  data = [],
  spec = {},
  height = 350,
  showBrush = true,
  showZoomControls = true,
}) {
  const { type = 'bar', xField, yFields = [], title } = spec

  const {
    chartRef,
    exporting,
    zoomState,
    displayData,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    handleResetZoom,
    handleExportChart,
    handleBrushChange,
  } = useZoomableChart({ data, spec, title })

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          {title && (
            <Typography variant="subtitle1" fontWeight={600}>
              {title}
            </Typography>
          )}
          <Chip label={type.toUpperCase()} size="small" variant="outlined" />
          {zoomState.isZoomed && (
            <Chip label="Zoomed" size="small" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
          )}
        </Stack>

        <Stack direction="row" spacing={0.5} alignItems="center">
          <MuiTooltip title="Export chart as PNG">
            <IconButton
              size="small"
              onClick={handleExportChart}
              disabled={exporting}
            >
              {exporting ? (
                <CircularProgress size={16} />
              ) : (
                <DownloadIcon fontSize="small" />
              )}
            </IconButton>
          </MuiTooltip>
          {showZoomControls && type !== 'pie' && (
            <>
              <IconButton
                size="small"
                onClick={handleResetZoom}
                disabled={!zoomState.isZoomed}
                title="Reset zoom"
              >
                <ZoomOutMapIcon fontSize="small" />
              </IconButton>
              <Typography variant="caption" color="text.secondary">
                Drag to zoom
              </Typography>
            </>
          )}
        </Stack>
      </Stack>

      <Box ref={chartRef} sx={{ width: '100%', height }}>
        <ResponsiveContainer width="100%" height="100%">
          <ChartRenderer
            type={type}
            xField={xField}
            yFields={yFields}
            displayData={displayData}
            data={data}
            height={height}
            showBrush={showBrush}
            zoomState={zoomState}
            handleMouseDown={handleMouseDown}
            handleMouseMove={handleMouseMove}
            handleMouseUp={handleMouseUp}
            handleBrushChange={handleBrushChange}
          />
        </ResponsiveContainer>
      </Box>

      {spec.description && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {spec.description}
        </Typography>
      )}
    </Box>
  )
}
