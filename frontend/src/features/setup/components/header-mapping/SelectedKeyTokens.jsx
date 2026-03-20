import {
  Box,
  Chip,
  Stack,
  Typography,
} from "@mui/material";
import { neutral } from "@/app/theme";

export default function SelectedKeyTokens({
  orderedKeyTokens,
  waiting,
  onToggleKey,
}) {
  return (
    <Box sx={{ mt: 1 }}>
      <Typography variant="subtitle2">Selected Key Tokens</Typography>
      {orderedKeyTokens.length ? (
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mt: 0.75 }}>
          {orderedKeyTokens.map((token) => (
            <Chip
              key={`key-token-${token}`}
              label={token}
              size="small"
              onDelete={waiting ? undefined : () => onToggleKey(token, false)}
              sx={{
                bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                color: 'common.white',
                '& .MuiChip-deleteIcon': { color: 'common.white', opacity: 0.7 },
              }}
            />
          ))}
        </Stack>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Toggle rows below to mark required key filters.
        </Typography>
      )}
    </Box>
  );
}
