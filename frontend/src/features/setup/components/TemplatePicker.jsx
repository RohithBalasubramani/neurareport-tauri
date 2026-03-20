import { useMemo } from 'react'
import { alpha, Collapse, LinearProgress } from '@mui/material'
import { neutral } from '@/app/theme'
import Surface from '@/components/layout/Surface.jsx'
import { surfaceStackSx } from '../utils/templatesPaneUtils'
import { useSetupTemplatePicker } from '../hooks/useSetupTemplatePicker'
import SetupTemplateToolbar from './template-picker/SetupTemplateToolbar.jsx'
import SetupTemplateList from './template-picker/SetupTemplateList.jsx'
import TemplatePreviewDialog from './template-picker/TemplatePreviewDialog.jsx'

function TemplatePicker({ selected, onToggle, tagFilter, setTagFilter }) {
  const picker = useSetupTemplatePicker({ selected, onToggle })

  const filtered = useMemo(
    () => picker.getFiltered(tagFilter),
    [picker.getFiltered, tagFilter],
  )

  return (
    <Surface sx={surfaceStackSx}>
      <SetupTemplateToolbar
        selected={selected}
        filtered={filtered}
        allTags={picker.allTags}
        tagFilter={tagFilter}
        setTagFilter={setTagFilter}
        nameQuery={picker.nameQuery}
        setNameQuery={picker.setNameQuery}
        importing={picker.importing}
        fileInputRef={picker.fileInputRef}
        onImportClick={picker.handleImportClick}
        onImportInputChange={picker.handleImportInputChange}
      />
      <Collapse in={picker.isFetching && !picker.isLoading} unmountOnExit>
        <LinearProgress sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] }, borderRadius: 1 }} aria-label="Refreshing templates" />
      </Collapse>
      <SetupTemplateList
        templates={picker.templates}
        filtered={filtered}
        isLoading={picker.isLoading}
        isFetching={picker.isFetching}
        tagFilter={tagFilter}
        nameQuery={picker.nameQuery}
        selected={selected}
        deleting={picker.deleting}
        onToggle={onToggle}
        onDelete={picker.handleDeleteTemplate}
        onThumbClick={picker.handleThumbClick}
        getTemplateCardData={picker.getTemplateCardData}
        setSetupNav={picker.setSetupNav}
      />
      <TemplatePreviewDialog
        open={picker.previewOpen}
        onClose={picker.handlePreviewClose}
        src={picker.previewSrc}
        type={picker.previewType}
        previewKey={picker.previewKey}
      />
    </Surface>
  )
}

export default TemplatePicker
