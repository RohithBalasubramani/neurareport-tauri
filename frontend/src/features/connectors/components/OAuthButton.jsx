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
} from '@mui/material'
import {
  Cloud as CloudIcon,
  CheckCircle as ConnectedIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { getOAuthPopupUrl } from '@/api/connectors'
import { neutral } from '@/app/theme'
import { OAUTH_PROVIDERS, isOAuthProvider, getProviderConfig } from './oauthProviderConfig'
import { OAuthButtonStyled } from './oauthButtonStyles'

export { isOAuthProvider, getProviderConfig }

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
  const isExpired = expiresAt && new Date(expiresAt) < new Date()

  useEffect(() => {
    const handleMessage = (event) => {
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
