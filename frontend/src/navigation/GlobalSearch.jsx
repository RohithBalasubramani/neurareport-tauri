/**
 * Premium Global Search
 * Command palette style search with theme-based styling
 */
import {
  Box,
  TextField,
  InputAdornment,
  Popper,
  Paper,
  List,
  Typography,
  CircularProgress,
  useTheme,
  alpha,
  ClickAwayListener,
  keyframes,
} from '@mui/material'
import { neutral } from '@/app/theme'
import SearchIcon from '@mui/icons-material/Search'
import KeyboardIcon from '@mui/icons-material/Keyboard'
import { useGlobalSearchState } from './hooks/useGlobalSearch'
import SearchResult from './components/SearchResult'

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

export default function GlobalSearch({
  variant = 'compact',
  enableShortcut = true,
  showShortcutHint = true,
  placeholder,
}) {
  const theme = useTheme()
  const inputPlaceholder = placeholder || (enableShortcut ? 'Search... (Ctrl+K)' : 'Search...')
  const isCompact = variant === 'compact'

  const {
    query, results, loading, open, selectedIndex,
    inputRef, anchorRef,
    handleSelect, handleKeyDown, handleInputChange,
    handleFocus, handleClickAway,
  } = useGlobalSearchState({ enableShortcut })

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
      <Box ref={anchorRef} sx={{ position: 'relative', width: isCompact ? 240 : 320 }}>
        <TextField
          inputRef={inputRef}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder={inputPlaceholder}
          size="small"
          fullWidth
          data-testid="global-search-input"
          inputProps={{ 'aria-label': 'Search' }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                {loading ? (
                  <CircularProgress size={16} sx={{ color: theme.palette.text.secondary }} />
                ) : (
                  <SearchIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
                )}
              </InputAdornment>
            ),
            endAdornment: isCompact && showShortcutHint && enableShortcut && (
              <InputAdornment position="end">
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.25,
                    px: 0.5,
                    py: 0.25,
                    bgcolor: alpha(theme.palette.text.primary, 0.08),
                    borderRadius: 1,  // Figma spec: 8px
                  }}
                >
                  <KeyboardIcon sx={{ fontSize: 12, color: theme.palette.text.disabled }} />
                  <Typography sx={{ fontSize: '0.625rem', color: theme.palette.text.disabled }}>K</Typography>
                </Box>
              </InputAdornment>
            ),
            sx: {
              bgcolor: alpha(theme.palette.background.paper, 0.5),
              borderRadius: 1,  // Figma spec: 8px
              transition: 'all 0.2s ease',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: alpha(theme.palette.divider, 0.15),
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: alpha(theme.palette.divider, 0.3),
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
              },
              '& input': {
                fontSize: '14px',
                color: theme.palette.text.primary,
                '&::placeholder': {
                  color: theme.palette.text.secondary,
                  opacity: 1,
                },
              },
            },
          }}
        />

        <Popper
          open={open}
          anchorEl={anchorRef.current}
          placement="bottom-start"
          style={{ width: anchorRef.current?.offsetWidth || 300, zIndex: 1300 }}
        >
          <Paper
            sx={{
              mt: 0.5,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.background.paper, 0.92) : 'rgba(255, 255, 255, 0.92)',
              backdropFilter: 'blur(12px)',
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
              borderRadius: 1,  // Figma spec: 8px
              boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}`,
              maxHeight: 400,
              overflow: 'auto',
              animation: `${fadeInUp} 0.2s ease-out`,
            }}
          >
            {results.length === 0 ? (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography sx={{ color: theme.palette.text.secondary, fontSize: '14px' }}>
                  No results found
                </Typography>
              </Box>
            ) : (
              <List disablePadding>
                {results.map((result, index) => (
                  <SearchResult
                    key={`${result.type}-${result.id}`}
                    result={result}
                    onSelect={handleSelect}
                    isSelected={index === selectedIndex}
                  />
                ))}
              </List>
            )}
          </Paper>
        </Popper>
      </Box>
    </ClickAwayListener>
  )
}
