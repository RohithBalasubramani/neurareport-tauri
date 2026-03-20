import Grid from '@mui/material/Grid2'
import { Card, CardContent, Stack, Typography } from '@mui/material'

export default function StarterGrid({ list }) {
  return (
    <Grid container spacing={2.5}>
      {list.map((t) => (
        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={t.id} sx={{ minWidth: 0 }}>
          <Card variant="outlined">
            <CardContent>
              <Stack spacing={1}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {t.name || t.id}
                </Typography>
                {t.description && (
                  <Typography variant="body2" color="text.secondary">
                    {t.description}
                  </Typography>
                )}
                <Typography variant="caption" color="text.secondary">
                  Starter template - Read-only
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  )
}
