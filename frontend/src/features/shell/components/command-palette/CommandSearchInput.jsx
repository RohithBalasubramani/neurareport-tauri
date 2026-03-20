import {
  Box,
  TextField,
  InputAdornment,
  CircularProgress,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'

export default function CommandSearchInput({ inputRef, query, setQuery, onKeyDown, isSearching }) {
  return (
    <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
      <TextField
        ref={inputRef}
        fullWidth
        placeholder="Search commands, templates, connections..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={onKeyDown}
        autoFocus
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              {isSearching ? (
                <CircularProgress size={20} sx={{ color: 'text.secondary' }} />
              ) : (
                <SearchIcon sx={{ color: 'text.secondary' }} />
              )}
            </InputAdornment>
          ),
          sx: {
            '& .MuiOutlinedInput-notchedOutline': {
              border: 'none',
            },
          },
        }}
        sx={{
          '& .MuiInputBase-root': {
            bgcolor: 'action.hover',
            borderRadius: 1,
          },
        }}
      />
    </Box>
  )
}
