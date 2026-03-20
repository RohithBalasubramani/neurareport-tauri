import Grid from '@mui/material/Grid2'
import { Box, Button } from '@mui/material'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import LoadingState from '@/components/feedback/LoadingState.jsx'
import SetupTemplateCard from './SetupTemplateCard.jsx'

export default function SetupTemplateList({
  templates,
  filtered,
  isLoading,
  isFetching,
  tagFilter,
  nameQuery,
  selected,
  deleting,
  onToggle,
  onDelete,
  onThumbClick,
  getTemplateCardData,
  setSetupNav,
}) {
  if (!templates.length && (isLoading || isFetching)) {
    return (
      <Box sx={{ py: 6, display: 'flex', justifyContent: 'center' }}>
        <LoadingState label="Loading templates..." description="Fetching approved templates from the server." />
      </Box>
    )
  }

  if (!filtered.length) {
    return (
      <EmptyState
        title={tagFilter.length || nameQuery.trim() ? 'No templates match the filters' : 'No approved templates yet'}
        description={tagFilter.length || nameQuery.trim()
          ? 'Adjust the filters or clear them to see all approved templates.'
          : 'Upload and verify a template to make it available for runs.'}
        action={
          !filtered.length && !templates.length ? (
            <Button variant="contained" onClick={() => setSetupNav('generate')}>
              Upload template
            </Button>
          ) : null
        }
      />
    )
  }

  return (
    <Grid container spacing={2}>
      {filtered.map((t) => {
        const selectedState = selected.includes(t.id)
        const cardData = getTemplateCardData(t)
        return (
          <SetupTemplateCard
            key={t.id}
            template={t}
            selectedState={selectedState}
            deleting={deleting}
            cardData={cardData}
            onToggle={onToggle}
            onDelete={onDelete}
            onThumbClick={onThumbClick}
          />
        )
      })}
    </Grid>
  )
}
