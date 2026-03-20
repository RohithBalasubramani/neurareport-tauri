/**
 * Premium Settings Page
 * Slim orchestrator — state lives in useSettingsState hook,
 * UI sections are separate components.
 */
import {
  Box,
  Typography,
  Stack,
  CircularProgress,
  Alert,
  useTheme,
  styled,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import { fadeInUp, RefreshButton } from '@/styles'
import { useSettingsState } from '../hooks/useSettingsState'
import PersonalSettingsCard from '../components/PersonalSettingsCard'
import SecurityCard from '../components/SecurityCard'
import { SystemStatusCard, StorageCard, ApiConfigCard, LlmProviderCard } from '../components/SystemStatusCard'
import SmtpCard from '../components/SmtpCard'
import TokenUsageCard from '../components/TokenUsageCard'
import PreferencesCard, { ExportCard } from '../components/PreferencesCard'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 1000,
  margin: '0 auto',
  width: '100%',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}))

const HeaderContainer = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out`,
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function SettingsPage() {
  const theme = useTheme()
  const state = useSettingsState()

  return (
    <PageContainer>
      {/* Header */}
      <HeaderContainer direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h5" fontWeight={600} sx={{ color: theme.palette.text.primary }}>
            Settings
          </Typography>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            System configuration and preferences
          </Typography>
        </Box>
        <RefreshButton
          onClick={state.fetchHealth}
          disabled={state.loading}
          sx={{ color: theme.palette.text.secondary }}
        >
          {state.loading ? <CircularProgress size={20} /> : <RefreshIcon />}
        </RefreshButton>
      </HeaderContainer>

      {state.error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 1 }}>
          {state.error}
        </Alert>
      )}

      <Stack spacing={3}>
        <PersonalSettingsCard
          selectedLanguage={state.selectedLanguage}
          selectedTimezone={state.selectedTimezone}
          onLanguageChange={state.handleLanguageChange}
          onTimezoneChange={state.handleTimezoneChange}
        />

        <SecurityCard
          twoFactorEnabled={state.twoFactorEnabled}
          setTwoFactorEnabled={state.setTwoFactorEnabled}
          showTwoFactorSetup={state.showTwoFactorSetup}
          setShowTwoFactorSetup={state.setShowTwoFactorSetup}
          onTwoFactorToggle={state.handleTwoFactorToggle}
        />

        <SystemStatusCard health={state.health} />
        <StorageCard uploadsDir={state.uploadsDir} stateDir={state.stateDir} memory={state.memory} />
        <ApiConfigCard config={state.config} />
        <LlmProviderCard llm={state.llm} />

        <SmtpCard
          smtp={state.smtp}
          smtpLoading={state.smtpLoading}
          smtpTesting={state.smtpTesting}
          showSmtpPassword={state.showSmtpPassword}
          setShowSmtpPassword={state.setShowSmtpPassword}
          onSmtpSave={state.handleSmtpSave}
          onSmtpTest={state.handleSmtpTest}
          onSmtpChange={state.handleSmtpChange}
        />

        <TokenUsageCard tokenUsage={state.tokenUsage} />

        <ExportCard
          exporting={state.exporting}
          onExportConfig={state.handleExportConfig}
        />

        <PreferencesCard
          preferences={state.preferences}
          demoMode={state.demoMode}
          onDemoModeChange={state.handleDemoModeChange}
          onPrefChange={state.handlePrefChange}
        />
      </Stack>
    </PageContainer>
  )
}
