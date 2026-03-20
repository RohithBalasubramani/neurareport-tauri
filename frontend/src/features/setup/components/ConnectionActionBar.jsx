import {
  Stack, Button, Typography, Chip,
  FormControlLabel, Checkbox,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import { Controller } from 'react-hook-form'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import { neutral } from '@/app/theme'

export default function ConnectionActionBar({
  isSQLite, mutation, canSave, handleSave,
  showDetails, setShowDetails, control, connection,
}) {
  return (
    <Stack
      direction={{ xs: 'column', md: 'row' }}
      spacing={1.5}
      alignItems={{ xs: 'stretch', md: 'center' }}
      sx={{ flexWrap: 'wrap', rowGap: 1.5 }}
    >
      <Stack
        direction="row"
        spacing={1}
        alignItems="center"
        sx={{ flexWrap: 'wrap' }}
      >
        <Button
          variant="contained"
          disableElevation
          startIcon={<PlayArrowIcon />}
          sx={{ borderRadius: 1, px: 2.5, textTransform: 'none', bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
          type="submit"
          disabled={mutation.isPending}
        >
          Test Connection
        </Button>
        <Button
          variant="outlined"
          type="button"
          onClick={handleSave}
          disabled={mutation.isPending || !canSave}
          startIcon={<ArrowForwardIcon />}
          sx={{ color: 'text.secondary', borderColor: (theme) => alpha(theme.palette.text.secondary, 0.3), '&:hover': { borderColor: 'text.secondary' } }}
        >
          Save & Continue
        </Button>
      </Stack>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap' }}>
        {mutation.isPending && (
          <Typography variant="body2" color="text.secondary" role="status" aria-live="polite">
            Testing connection...
          </Typography>
        )}
        {connection.status === 'connected' && (
          <Chip
            label="Connected"
            size="small"
            onClick={() => setShowDetails((v) => !v)}
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
        )}
        {connection.status === 'failed' && (
          <Chip
            label="Failed"
            size="small"
            onClick={() => setShowDetails((v) => !v)}
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
        )}
      </Stack>
      {!isSQLite && (
        <Controller
          name="ssl"
          control={control}
          render={({ field }) => (
            <FormControlLabel
              sx={{ m: 0, whiteSpace: 'nowrap' }}
              componentsProps={{
                typography: {
                  sx: (theme) => ({
                    whiteSpace: 'nowrap',
                    fontWeight: theme.typography.fontWeightBold,
                  }),
                },
              }}
              control={
                <Checkbox
                  size="small"
                  checked={Boolean(field.value)}
                  onChange={(event) => field.onChange(event.target.checked)}
                />
              }
              label="Use SSL"
            />
          )}
        />
      )}
    </Stack>
  )
}
