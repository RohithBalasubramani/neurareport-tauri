/**
 * Connectors Page Container
 * Database and cloud storage connector management.
 */
import React from 'react'
import {
  Box,
  Typography,
  Chip,
  Alert,
  Tabs,
  Tab,
  Card,
  Button,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  CheckCircle as ConnectedIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { useConnectorsPage } from '../hooks/useConnectorsPage'
import AvailableConnectorsTab from '../components/AvailableConnectorsTab'
import MyConnectionsTab from '../components/MyConnectionsTab'
import { ConnectDialog, QueryDialog, SchemaDialog } from '../components/ConnectorDialogs'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const Header = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

const Content = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(3),
}))

const ConnectorCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: `0 8px 30px ${alpha(theme.palette.text.primary, 0.15)}`,
  },
}))

const ConnectorIcon = styled(Box)(({ theme }) => ({
  width: 48,
  height: 48,
  borderRadius: 8,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(2),
}))

const StatusChip = styled(Chip)(({ theme, status }) => ({
  borderRadius: 6,
  fontWeight: 500,
  ...(status === 'connected' && {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    color: theme.palette.text.secondary,
  }),
  ...(status === 'error' && {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    color: theme.palette.text.secondary,
  }),
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ConnectorsPage() {
  const theme = useTheme()
  const c = useConnectorsPage()

  return (
    <PageContainer>
      <Header>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Data Connectors
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Connect to databases and cloud storage services
            </Typography>
          </Box>
          <Chip
            label={`${c.connections.length} connections`}
            variant="outlined"
            sx={{ borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700], color: 'text.secondary' }}
          />
        </Box>

        <Tabs
          value={c.activeTab}
          onChange={(e, v) => c.handleTabChange(v)}
          sx={{ mt: 2 }}
        >
          <Tab label="Available Connectors" />
          <Tab label={`My Connections (${c.connections.length})`} />
        </Tabs>
      </Header>

      <Content>
        {c.activeTab === 0 ? (
          <AvailableConnectorsTab
            handleOpenConnect={c.handleOpenConnect}
            ConnectorCard={ConnectorCard}
            ConnectorIcon={ConnectorIcon}
            ActionButton={ActionButton}
          />
        ) : (
          <MyConnectionsTab
            connections={c.connections}
            handleCheckHealth={c.handleCheckHealth}
            handleViewSchema={c.handleViewSchema}
            handleOpenQuery={c.handleOpenQuery}
            handleDeleteConnection={c.handleDeleteConnection}
            handleTabChange={c.handleTabChange}
            ConnectorCard={ConnectorCard}
            StatusChip={StatusChip}
            ActionButton={ActionButton}
            ConnectedIcon={ConnectedIcon}
            ErrorIcon={ErrorIcon}
          />
        )}
      </Content>

      <ConnectDialog
        open={c.connectDialogOpen}
        onClose={c.handleCloseConnect}
        selectedConnector={c.selectedConnector}
        connectionName={c.connectionName}
        setConnectionName={c.setConnectionName}
        connectionConfig={c.connectionConfig}
        setConnectionConfig={c.setConnectionConfig}
        onTest={c.handleTestConnection}
        onCreate={c.handleCreateConnection}
        testing={c.testing}
        loading={c.loading}
      />

      <QueryDialog
        open={c.queryDialogOpen}
        onClose={c.handleCloseQuery}
        queryText={c.queryText}
        setQueryText={c.setQueryText}
        queryResult={c.queryResult}
        onExecute={c.handleExecuteQuery}
        querying={c.querying}
      />

      <SchemaDialog
        open={c.schemaDialogOpen}
        onClose={c.handleCloseSchema}
        schema={c.schema}
      />

      {c.error && (
        <Alert
          severity="error"
          onClose={c.handleDismissError}
          sx={{ position: 'fixed', bottom: 16, right: 16, maxWidth: 400 }}
        >
          {c.error}
        </Alert>
      )}
    </PageContainer>
  )
}
