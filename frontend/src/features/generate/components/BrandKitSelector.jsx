/**
 * Brand kit autocomplete selector for Generate page.
 */
import { Box, Typography, Chip, Autocomplete, TextField } from '@mui/material'
import PaletteIcon from '@mui/icons-material/Palette'

export default function BrandKitSelector({ brandKits, selectedBrandKit, setSelectedBrandKit }) {
  if (!brandKits.length) return null

  return (
    <Autocomplete
      size="small"
      options={brandKits}
      value={selectedBrandKit}
      onChange={(_, kit) => setSelectedBrandKit(kit)}
      getOptionLabel={(kit) => kit.name || ''}
      isOptionEqualToValue={(opt, val) => opt?.id === val?.id}
      renderOption={(props, kit) => (
        <li {...props} key={kit.id}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 14, height: 14, borderRadius: '50%', bgcolor: kit.primary_color, border: '1px solid rgba(0,0,0,0.15)', flexShrink: 0 }} />
            <Typography variant="body2">{kit.name}</Typography>
            {kit.is_default && <Chip label="default" size="small" variant="outlined" sx={{ ml: 'auto', height: 18, fontSize: 11 }} />}
          </Box>
        </li>
      )}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Brand Kit"
          placeholder="Select brand kit for report styling"
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <>
                <PaletteIcon fontSize="small" sx={{ color: 'text.secondary', mr: 0.5 }} />
                {params.InputProps.startAdornment}
              </>
            ),
          }}
        />
      )}
      sx={{ maxWidth: 360 }}
    />
  )
}
