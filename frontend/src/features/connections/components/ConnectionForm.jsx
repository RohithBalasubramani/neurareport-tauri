import {
  Box,
  Stack,
  Button,
  Alert,
  Divider,
  CircularProgress,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import { useConnectionForm } from '../hooks/useConnectionForm'
import {
  ConnectionNameField,
  DbTypeField,
  HostPortFields,
  DatabaseField,
} from './ConnectionFormFields'
import { CredentialFields, AdvancedSettings } from './ConnectionFormAdvanced'

export default function ConnectionForm({ connection, onSave, onCancel, loading }) {
  const {
    formData,
    showAdvanced,
    setShowAdvanced,
    error,
    setError,
    touched,
    fieldErrors,
    testing,
    testResult,
    setTestResult,
    isSqlite,
    isFormValid,
    handleChange,
    handleBlur,
    handleDbTypeChange,
    handleTestConnection,
    handleSubmit,
  } = useConnectionForm(connection, onSave)

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Stack spacing={3}>
        {error && (
          <Alert
            severity="error"
            onClose={() => setError(null)}
            action={
              testResult === 'error' && (
                <Button color="inherit" size="small" onClick={handleTestConnection} disabled={testing}>
                  Try Again
                </Button>
              )
            }
          >
            {error}
          </Alert>
        )}

        <Alert severity="info">
          Use a read-only account when possible. Testing only checks connectivity. Saved credentials are encrypted for
          reuse. Deleting a connection never deletes data from your database.
        </Alert>

        <ConnectionNameField
          formData={formData}
          touched={touched}
          fieldErrors={fieldErrors}
          handleChange={handleChange}
          handleBlur={handleBlur}
        />

        <DbTypeField formData={formData} handleDbTypeChange={handleDbTypeChange} />

        {!isSqlite && (
          <HostPortFields
            formData={formData}
            touched={touched}
            fieldErrors={fieldErrors}
            handleChange={handleChange}
            handleBlur={handleBlur}
          />
        )}

        <DatabaseField
          formData={formData}
          isSqlite={isSqlite}
          touched={touched}
          fieldErrors={fieldErrors}
          handleChange={handleChange}
          handleBlur={handleBlur}
        />

        {!isSqlite && <CredentialFields formData={formData} handleChange={handleChange} />}

        <AdvancedSettings
          formData={formData}
          isSqlite={isSqlite}
          showAdvanced={showAdvanced}
          setShowAdvanced={setShowAdvanced}
          handleChange={handleChange}
        />

        <Divider />

        {testResult && (
          <Alert
            severity={testResult === 'success' ? 'success' : 'error'}
            icon={testResult === 'success' ? <CheckCircleIcon /> : <ErrorIcon />}
            onClose={() => setTestResult(null)}
            action={
              testResult === 'error' && (
                <Button color="inherit" size="small" onClick={handleTestConnection} disabled={testing}>
                  Retry
                </Button>
              )
            }
          >
            {testResult === 'success'
              ? 'Connection successful! Database is reachable.'
              : error || 'Connection failed. Check your settings and try again.'}
          </Alert>
        )}

        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <Button
            variant="text"
            onClick={handleTestConnection}
            disabled={loading || testing}
            startIcon={testing ? <CircularProgress size={16} /> : null}
          >
            {testing ? 'Testing...' : 'Test Connection'}
          </Button>
          <Button variant="outlined" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={loading || !isFormValid}>
            {connection ? 'Update Connection' : 'Add Connection'}
          </Button>
        </Stack>
      </Stack>
    </Box>
  )
}
