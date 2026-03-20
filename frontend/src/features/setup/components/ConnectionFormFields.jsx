import { Box, Alert, Collapse } from '@mui/material'
import { useAppStore } from '@/stores'
import FormErrorSummary from '@/components/form/FormErrorSummary.jsx'
import { FORM_FIELD_ORDER, FORM_FIELD_LABELS } from '../constants/connectDB'
import DbTypeSection from './DbTypeSection'
import { NameHostPortRow, SqlitePathDisplay, DbUserPassRow } from './ConnectionFieldRows'
import ConnectionActionBar from './ConnectionActionBar'

export default function ConnectionFormFields({
  formProps,
  showDetails,
  setShowDetails,
  canSave,
}) {
  const { connection } = useAppStore()
  const {
    register,
    handleSubmit,
    errors,
    control,
    isSQLite,
    sqliteResolvedPath,
    showPw,
    setShowPw,
    showErrorSummary,
    hostHelperText,
    portHelperText,
    usernameHelperText,
    passwordHelperText,
    portPlaceholder,
    mutation,
    onSubmit,
    handleSave,
    handleFocusErrorField,
    copySqlitePath,
  } = formProps

  return (
    <>
      <FormErrorSummary
        errors={errors}
        visible={showErrorSummary}
        fieldOrder={FORM_FIELD_ORDER}
        fieldLabels={FORM_FIELD_LABELS}
        onFocusField={handleFocusErrorField}
        description="Resolve the items below before testing or saving the connection."
        sx={{ mb: 2 }}
      />

      <Box component="form" onSubmit={handleSubmit(onSubmit)}>
        <DbTypeSection control={control} errors={errors} />
        <NameHostPortRow
          register={register}
          errors={errors}
          isSQLite={isSQLite}
          hostHelperText={hostHelperText}
          portHelperText={portHelperText}
          portPlaceholder={portPlaceholder}
        />
        <SqlitePathDisplay
          isSQLite={isSQLite}
          sqliteResolvedPath={sqliteResolvedPath}
          copySqlitePath={copySqlitePath}
        />
        <DbUserPassRow
          register={register}
          errors={errors}
          isSQLite={isSQLite}
          usernameHelperText={usernameHelperText}
          passwordHelperText={passwordHelperText}
          showPw={showPw}
          setShowPw={setShowPw}
        />
        <ConnectionActionBar
          isSQLite={isSQLite}
          mutation={mutation}
          canSave={canSave}
          handleSave={handleSave}
          showDetails={showDetails}
          setShowDetails={setShowDetails}
          control={control}
          connection={connection}
        />
      </Box>

      <Box>
        <Collapse in={showDetails}>
          {connection.status === 'failed' && (
            <Alert severity="error">{connection.lastMessage}</Alert>
          )}
        </Collapse>
      </Box>
    </>
  )
}
