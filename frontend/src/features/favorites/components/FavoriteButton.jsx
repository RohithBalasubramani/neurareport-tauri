/**
 * Premium Favorite Button
 * Star toggle with theme-based styling
 */
import { useState, useCallback, useEffect } from 'react'
import { IconButton, Tooltip, CircularProgress, useTheme, alpha } from '@mui/material'
import StarIcon from '@mui/icons-material/Star'
import StarBorderIcon from '@mui/icons-material/StarBorder'
import * as api from '@/api/client'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { neutral, palette } from '@/app/theme'

/**
 * A reusable favorite toggle button.
 * @param {Object} props
 * @param {string} props.entityType - 'templates' or 'connections'
 * @param {string} props.entityId - The ID of the entity
 * @param {boolean} [props.initialFavorite] - Initial favorite state (if known)
 * @param {function} [props.onToggle] - Callback when favorite is toggled (isFavorite) => void
 * @param {'small' | 'medium'} [props.size] - Button size
 */
export default function FavoriteButton({
  entityType,
  entityId,
  initialFavorite,
  onToggle,
  size = 'small',
}) {
  const theme = useTheme()
  const { execute } = useInteraction()
  const [isFavorite, setIsFavorite] = useState(initialFavorite ?? false)
  const [loading, setLoading] = useState(false)
  const [checked, setChecked] = useState(initialFavorite !== undefined)

  // Check favorite status on mount if not provided
  useEffect(() => {
    if (checked || !entityId) return

    let cancelled = false
    api.checkFavorite(entityType, entityId)
      .then((result) => {
        if (!cancelled) {
          setIsFavorite(result.isFavorite)
          setChecked(true)
        }
      })
      .catch(() => {
        // Ignore errors on initial check
        if (!cancelled) setChecked(true)
      })

    return () => { cancelled = true }
  }, [entityType, entityId, checked])

  // Update if initialFavorite prop changes
  useEffect(() => {
    if (initialFavorite !== undefined) {
      setIsFavorite(initialFavorite)
      setChecked(true)
    }
  }, [initialFavorite])

  const handleToggle = useCallback(async (e) => {
    e.stopPropagation()
    if (loading || !entityId) return

    setLoading(true)
    const nextFavorite = !isFavorite

    // Optimistic update
    setIsFavorite(nextFavorite)

    try {
      await execute({
        type: nextFavorite ? InteractionType.CREATE : InteractionType.DELETE,
        label: nextFavorite ? 'Add favorite' : 'Remove favorite',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        blocksNavigation: false,
        intent: {
          entityType,
          entityId,
          action: nextFavorite ? 'favorite_add' : 'favorite_remove',
        },
        action: async () => {
          try {
            if (nextFavorite) {
              await api.addFavorite(entityType, entityId)
            } else {
              await api.removeFavorite(entityType, entityId)
            }
            onToggle?.(nextFavorite)
          } catch (err) {
            // Revert on error
            setIsFavorite(!nextFavorite)
            throw err
          }
        },
      })
    } finally {
      setLoading(false)
    }
  }, [entityType, entityId, isFavorite, loading, onToggle, execute])

  const iconSize = size === 'small' ? 18 : 22

  return (
    <Tooltip title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}>
      <IconButton
        size={size}
        onClick={handleToggle}
        disabled={loading}
        data-testid="favorite-button"
        sx={{
          color: isFavorite ? (theme.palette.mode === 'dark' ? neutral[300] : neutral[900]) : theme.palette.text.secondary,
          transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': {
            color: theme.palette.mode === 'dark' ? neutral[300] : neutral[900],
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            transform: 'scale(1.1)',
          },
        }}
      >
        {loading ? (
          <CircularProgress size={iconSize - 4} sx={{ color: theme.palette.text.secondary }} />
        ) : isFavorite ? (
          <StarIcon sx={{ fontSize: iconSize }} />
        ) : (
          <StarBorderIcon sx={{ fontSize: iconSize }} />
        )}
      </IconButton>
    </Tooltip>
  )
}
