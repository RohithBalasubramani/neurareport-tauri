import Grid from '@mui/material/Grid2'
import { Box, Stack, Alert, Button } from '@mui/material'

import { useGeneratePage } from '../hooks/useGeneratePage'
import GeneratePageHeader from '../components/GeneratePageHeader.jsx'
import BrandKitSelector from '../components/BrandKitSelector.jsx'
import TemplatePicker from '../components/TemplatePicker.jsx'
import GenerateAndDownload from '../components/GenerateAndDownload.jsx'

export default function GeneratePage() {
  const g = useGeneratePage()

  return (
    <Box sx={{ py: 3, px: 3 }}>
      {/* Page Header */}
      <GeneratePageHeader selected={g.selected} approved={g.approved} />

      <Stack spacing={3}>

        {/* Connection Warning */}
        {!g.hasConnection && (
          <Alert
            severity="warning"
            action={
              <Button color="inherit" size="small" onClick={() => g.handleNavigate('/', 'Open dashboard')}>
                Go to Setup
              </Button>
            }
          >
            Connect to a database in Setup to generate reports with real data.
          </Alert>
        )}

        {/* Main Content */}
        <Grid container spacing={3}>
          <Grid size={12}>
            <TemplatePicker
              selected={g.selected}
              onToggle={g.onToggle}
              outputFormats={g.outputFormats}
              setOutputFormats={g.setOutputFormats}
              tagFilter={g.tagFilter}
              setTagFilter={g.setTagFilter}
              onEditTemplate={(tpl) => {
                if (!tpl?.id) return
                g.handleNavigate(
                  `/templates/${tpl.id}/edit`,
                  'Edit template',
                  { templateId: tpl.id },
                  { state: { from: '/generate' } }
                )
              }}
            />
          </Grid>
          {/* Brand Kit selector */}
          {g.brandKits.length > 0 && (
            <Grid size={12}>
              <BrandKitSelector
                brandKits={g.brandKits}
                selectedBrandKit={g.selectedBrandKit}
                setSelectedBrandKit={g.setSelectedBrandKit}
              />
            </Grid>
          )}

          <Grid size={12} sx={{ minWidth: 0 }}>
            <GenerateAndDownload
              selected={g.selectedTemplates.map((t) => t.id)}
              selectedTemplates={g.selectedTemplates}
              autoType={g.autoType}
              start={g.start}
              end={g.end}
              setStart={g.setStart}
              setEnd={g.setEnd}
              onFind={g.onFind}
              findDisabled={g.finding}
              finding={g.finding}
              results={g.results}
              onToggleBatch={g.onToggleBatch}
              onGenerate={g.onGenerate}
              canGenerate={g.canGenerate}
              generateLabel={g.generateLabel}
              generation={g.generation}
              generatorReady={g.generatorSummary.ready}
              generatorIssues={g.generatorSummary}
              keyValues={g.keyValues}
              onKeyValueChange={g.handleKeyValueChange}
              keysReady={g.keysReady}
              keyOptions={g.keyOptions}
              keyOptionsLoading={g.keyOptionsLoading}
              onResampleFilter={g.handleResampleFilter}
            />
          </Grid>
        </Grid>
      </Stack>
    </Box>
  )
}
