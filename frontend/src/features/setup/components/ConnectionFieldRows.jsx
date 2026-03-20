import {
  Stack, TextField, Typography, InputAdornment,
  IconButton, Grid, Tooltip,
} from '@mui/material'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import { gridItemSx, fieldSx } from './formFieldStyles'

export function NameHostPortRow({
  register, errors, isSQLite,
  hostHelperText, portHelperText, portPlaceholder,
}) {
  return (
    <Grid container spacing={2} sx={{ mb: 2 }}>
      <Grid size={{ xs: 12, sm: 4, md: 4, lg: 4 }} sx={gridItemSx}>
        <TextField
          label="Connection Name"
          placeholder="e.g. Reporting Warehouse"
          fullWidth
          required
          size="small"
          margin="dense"
          variant="outlined"
          inputProps={{ maxLength: 80 }}
          error={!!errors.name}
          helperText={errors.name?.message || 'Used to save this connection preset'}
          InputLabelProps={{ shrink: true }}
          sx={fieldSx}
          {...register('name')}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 4, md: 4, lg: 4 }} sx={gridItemSx}>
        <TextField
          label="Host"
          fullWidth
          size="small"
          margin="dense"
          variant="outlined"
          disabled={isSQLite}
          error={!!errors.host}
          helperText={hostHelperText}
          placeholder={isSQLite ? '' : 'db.example.com'}
          InputLabelProps={{ shrink: true }}
          sx={fieldSx}
          {...register('host')}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 4, md: 4, lg: 4 }} sx={gridItemSx}>
        <TextField
          label="Port"
          fullWidth
          size="small"
          margin="dense"
          variant="outlined"
          disabled={isSQLite}
          error={!!errors.port}
          helperText={portHelperText}
          placeholder={portPlaceholder}
          inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
          InputLabelProps={{ shrink: true }}
          sx={fieldSx}
          {...register('port')}
        />
      </Grid>
    </Grid>
  )
}

export function SqlitePathDisplay({ isSQLite, sqliteResolvedPath, copySqlitePath }) {
  if (!isSQLite || !sqliteResolvedPath) return null
  return (
    <Stack
      direction={{ xs: 'column', sm: 'row' }}
      spacing={1}
      alignItems={{ xs: 'flex-start', sm: 'center' }}
      sx={{ mb: 2, backgroundColor: 'background.default', borderRadius: 1, px: 1.5, py: 1.25, border: '1px solid', borderColor: 'divider' }}
    >
      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
        Resolved path:
      </Typography>
      <Typography
        variant="caption"
        sx={{
          fontFamily: 'var(--font-mono, monospace)',
          color: 'text.primary',
          wordBreak: 'break-all',
        }}
      >
        {sqliteResolvedPath}
      </Typography>
      <Tooltip title="Copy resolved path">
        <IconButton
          size="small"
          onClick={copySqlitePath}
          aria-label="Copy resolved path"
          sx={{ color: 'text.secondary' }}
        >
          <ContentCopyIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Stack>
  )
}

export function DbUserPassRow({
  register, errors, isSQLite,
  usernameHelperText, passwordHelperText,
  showPw, setShowPw,
}) {
  return (
    <Grid container spacing={2} alignItems="flex-start" sx={{ mb: 2 }}>
      <Grid size={{ xs: 12, sm: 4, md: 4 }} sx={gridItemSx}>
        <TextField
          label="Database"
          placeholder={isSQLite ? 'Path to .db file' : 'Database name'}
          fullWidth
          size="small"
          margin="dense"
          variant="outlined"
          error={!!errors.db_name}
          helperText={errors.db_name?.message || ' '}
          InputLabelProps={{ shrink: true }}
          sx={fieldSx}
          {...register('db_name')}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 4, md: 4 }} sx={gridItemSx}>
        <TextField
          label="Username"
          fullWidth
          size="small"
          margin="dense"
          variant="outlined"
          disabled={isSQLite}
          error={!!errors.username}
          helperText={usernameHelperText}
          InputLabelProps={{ shrink: true }}
          sx={fieldSx}
          {...register('username')}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 4, md: 4 }} sx={gridItemSx}>
        <TextField
          label="Password"
          type={showPw ? 'text' : 'password'}
          fullWidth
          size="small"
          margin="dense"
          variant="outlined"
          disabled={isSQLite}
          error={!!errors.password}
          helperText={passwordHelperText}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={() => setShowPw(v => !v)} edge="end" aria-label="toggle password visibility">
                  {showPw ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
          InputLabelProps={{ shrink: true }}
          sx={fieldSx}
          {...register('password')}
        />
      </Grid>
    </Grid>
  )
}
