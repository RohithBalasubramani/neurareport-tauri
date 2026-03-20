import { Box, Alert } from '@mui/material'
import SensorsIcon from '@mui/icons-material/Sensors'
import PageHeader from '@/components/layout/PageHeader'
import { useLoggerPage } from '../hooks/useLoggerPage'
import LoggerToolbar from '../components/LoggerToolbar'
import LoggerPluginView from '../components/LoggerPluginView'
import LoggerDataView from '../components/LoggerDataView'

export default function LoggerPageContainer() {
  const state = useLoggerPage()

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <PageHeader
        title="Logger"
        subtitle="PLC data logger — device management, schemas, and data pipeline"
        icon={<SensorsIcon />}
      />

      <Box sx={{ px: 4, py: 2, maxWidth: 1400, mx: 'auto', width: '100%', flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Toolbar */}
        <LoggerToolbar
          viewMode={state.viewMode}
          setViewMode={state.setViewMode}
          loggerStatus={state.loggerStatus}
          handleRefreshIframe={state.handleRefreshIframe}
          loggerConnections={state.loggerConnections}
          selectedConnectionId={state.selectedConnectionId}
          handleConnectionSelect={state.handleConnectionSelect}
          discovering={state.discovering}
          handleDiscover={state.handleDiscover}
        />

        {state.discoveryError && (
          <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }} onClose={() => state.setDiscoveryError(null)}>
            {state.discoveryError}
          </Alert>
        )}

        {/* Plugin View — embedded Logger frontend */}
        {state.viewMode === 'plugin' && (
          <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
            <LoggerPluginView
              loggerStatus={state.loggerStatus}
              iframeRef={state.iframeRef}
              handleRetryConnection={state.handleRetryConnection}
            />
          </Box>
        )}

        {/* Data Pipeline View */}
        {state.viewMode === 'data' && (
          <LoggerDataView
            selectedConnectionId={state.selectedConnectionId}
            loggerConnections={state.loggerConnections}
            discovering={state.discovering}
            handleDiscover={state.handleDiscover}
          />
        )}
      </Box>
    </Box>
  )
}
