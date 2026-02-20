/**
 * OAuth Button Component
 * Handles OAuth authentication flow for cloud connectors.
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import {
  Button,
  CircularProgress,
  Box,
  Typography,
  Tooltip,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Google as GoogleIcon,
  Cloud as CloudIcon,
  CheckCircle as ConnectedIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { getOAuthPopupUrl } from '@/api/connectors'
import { neutral, palette, secondary } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const OAuthButtonStyled = styled(Button, {
  shouldForwardProp: (prop) => !['connected', 'providerColor'].includes(prop),
})(({ theme, connected, providerColor }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  padding: theme.spacing(1.5, 3),
  backgroundColor: connected
    ? alpha(theme.palette.text.secondary, 0.05)
    : alpha(providerColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.1),
  color: connected
    ? theme.palette.text.secondary
    : providerColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
  border: `1px solid ${alpha(connected ? theme.palette.text.secondary : providerColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.3)}`,
  '&:hover': {
    backgroundColor: alpha(connected ? theme.palette.text.secondary : providerColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.15),
  },
  '&:disabled': {
    opacity: 0.6,
  },
}))

// =============================================================================
// PROVIDER CONFIGS
// =============================================================================

const OAUTH_PROVIDERS = {
  google_drive: {
    name: 'Google Drive',
    icon: GoogleIcon,
    color: secondary.cyan[500],
    scopes: ['drive.readonly', 'drive.file'],
  },
  dropbox: {
    name: 'Dropbox',
    icon: CloudIcon,
    color: secondary.violet[500],
    scopes: ['files.content.read', 'files.content.write'],
  },
  onedrive: {
    name: 'OneDrive',
    icon: CloudIcon,
    color: secondary.slate[500],
    scopes: ['Files.Read', 'Files.ReadWrite'],
  },
  s3: {
    name: 'Amazon S3',
    icon: CloudIcon,
    color: secondary.fuchsia[500],
    scopes: [],
    // S3 uses access keys, not OAuth
    authType: 'credentials',
  },
  azure_blob: {
    name: 'Azure Blob',
    icon: CloudIcon,
    color: secondary.teal[500],
    scopes: [],
    // Azure can use connection strings or OAuth
    authType: 'mixed',
  },
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function OAuthButton({
  provider,
  connected = false,
  expiresAt = null,
  onConnect,
  onDisconnect,
  onRefreshToken,
  disabled = false,
}) {
  const theme = useTheme()
  const { execute } = useInteraction()
  const [loading, setLoading] = useState(false)
  const [authWindow, setAuthWindow] = useState(null)
  const checkClosedRef = useRef(null)

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (checkClosedRef.current) clearInterval(checkClosedRef.current)
    }
  }, [])

  const config = OAUTH_PROVIDERS[provider] || {
    name: provider,
    icon: CloudIcon,
    color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    scopes: [],
  }

  const ProviderIcon = config.icon

  // Check if token is expired
  const isExpired = expiresAt && new Date(expiresAt) < new Date()

  // Listen for OAuth callback
  useEffect(() => {
    const handleMessage = (event) => {
      // Verify origin for security
      if (event.origin !== window.location.origin) return

      if (event.data?.type === 'oauth_callback' && event.data?.provider === provider) {
        setLoading(false)
        if (event.data.success) {
          onConnect?.({
            access_token: event.data.access_token,
            refresh_token: event.data.refresh_token,
            expires_at: event.data.expires_at,
          })
        }
        authWindow?.close()
        setAuthWindow(null)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [authWindow, onConnect, provider])

  const handleConnect = useCallback(() => {
    if (connected) {
      return execute({
        type: InteractionType.DELETE,
        label: `Disconnect ${config.name}`,
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        intent: { provider, action: 'disconnect' },
        action: () => onDisconnect?.(),
      })
    }

    return execute({
      type: InteractionType.EXECUTE,
      label: `Connect ${config.name}`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      intent: { provider, action: 'connect' },
      action: async () => {
        setLoading(true)

        try {
          const { auth_url } = await getOAuthPopupUrl(provider)

          const width = 600
          const height = 700
          const left = window.screenX + (window.outerWidth - width) / 2
          const top = window.screenY + (window.outerHeight - height) / 2

          const popup = window.open(
            auth_url,
            `oauth_${provider}`,
            `width=${width},height=${height},left=${left},top=${top}`
          )

          setAuthWindow(popup)

          checkClosedRef.current = setInterval(() => {
            if (popup?.closed) {
              setLoading(false)
              clearInterval(checkClosedRef.current)
              checkClosedRef.current = null
            }
          }, 500)
        } catch (error) {
          setLoading(false)
          throw error
        }
      },
    })
  }, [connected, config.name, execute, onDisconnect, provider])

  const handleRefresh = useCallback(() => {
    return execute({
      type: InteractionType.UPDATE,
      label: `Refresh ${config.name} token`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      intent: { provider, action: 'refresh-token' },
      action: async () => {
        setLoading(true)
        try {
          await onRefreshToken?.()
        } finally {
          setLoading(false)
        }
      },
    })
  }, [config.name, execute, onRefreshToken, provider])

  // For non-OAuth providers (S3, etc.)
  if (config.authType === 'credentials') {
    return (
      <Box>
        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
          {config.name} uses access keys for authentication
        </Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <OAuthButtonStyled
        onClick={handleConnect}
        disabled={disabled || loading}
        connected={connected}
        providerColor={config.color}
        startIcon={
          loading ? (
            <CircularProgress size={18} />
          ) : connected ? (
            <ConnectedIcon />
          ) : (
            <ProviderIcon />
          )
        }
      >
        {connected ? `Connected to ${config.name}` : `Connect ${config.name}`}
      </OAuthButtonStyled>

      {connected && isExpired && (
        <Tooltip title="Token expired - click to refresh">
          <Button
            size="small"
            onClick={handleRefresh}
            disabled={loading}
            sx={{ minWidth: 'auto' }}
          >
            <RefreshIcon fontSize="small" />
          </Button>
        </Tooltip>
      )}
    </Box>
  )
}

/**
 * Check if a provider uses OAuth
 */
export function isOAuthProvider(provider) {
  const config = OAUTH_PROVIDERS[provider]
  return config && config.authType !== 'credentials'
}

/**
 * Get provider configuration
 */
export function getProviderConfig(provider) {
  return OAUTH_PROVIDERS[provider] || null
}
