// =============================================================================
// FIELD CONFIGS BY CONNECTOR TYPE
// =============================================================================

export const CONNECTOR_FIELDS = {
  // Databases
  postgresql: {
    name: 'PostgreSQL',
    fields: [
      { name: 'host', label: 'Host', type: 'text', required: true, default: 'localhost' },
      { name: 'port', label: 'Port', type: 'number', required: true, default: 5432 },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'password', label: 'Password', type: 'password', required: true },
      { name: 'ssl', label: 'Use SSL', type: 'boolean', default: true },
    ],
    advanced: [
      { name: 'sslmode', label: 'SSL Mode', type: 'select', options: ['disable', 'require', 'verify-ca', 'verify-full'], default: 'require' },
      { name: 'connect_timeout', label: 'Connection Timeout (s)', type: 'number', default: 10 },
    ],
  },
  mysql: {
    name: 'MySQL',
    fields: [
      { name: 'host', label: 'Host', type: 'text', required: true, default: 'localhost' },
      { name: 'port', label: 'Port', type: 'number', required: true, default: 3306 },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'password', label: 'Password', type: 'password', required: true },
      { name: 'ssl', label: 'Use SSL', type: 'boolean', default: false },
    ],
    advanced: [
      { name: 'charset', label: 'Charset', type: 'text', default: 'utf8mb4' },
      { name: 'connect_timeout', label: 'Connection Timeout (s)', type: 'number', default: 10 },
    ],
  },
  mongodb: {
    name: 'MongoDB',
    fields: [
      { name: 'host', label: 'Host', type: 'text', required: true, default: 'localhost' },
      { name: 'port', label: 'Port', type: 'number', required: true, default: 27017 },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text' },
      { name: 'password', label: 'Password', type: 'password' },
      { name: 'auth_source', label: 'Auth Source', type: 'text', default: 'admin' },
    ],
    advanced: [
      { name: 'replica_set', label: 'Replica Set', type: 'text' },
      { name: 'tls', label: 'Use TLS', type: 'boolean', default: false },
    ],
  },
  sqlserver: {
    name: 'SQL Server',
    fields: [
      { name: 'host', label: 'Host', type: 'text', required: true },
      { name: 'port', label: 'Port', type: 'number', required: true, default: 1433 },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'password', label: 'Password', type: 'password', required: true },
      { name: 'encrypt', label: 'Encrypt Connection', type: 'boolean', default: true },
    ],
    advanced: [
      { name: 'trust_server_certificate', label: 'Trust Server Certificate', type: 'boolean', default: false },
    ],
  },
  bigquery: {
    name: 'BigQuery',
    fields: [
      { name: 'project_id', label: 'Project ID', type: 'text', required: true },
      { name: 'dataset', label: 'Dataset', type: 'text' },
      { name: 'credentials_json', label: 'Service Account JSON', type: 'textarea', required: true },
    ],
    advanced: [
      { name: 'location', label: 'Location', type: 'text', default: 'US' },
    ],
  },
  snowflake: {
    name: 'Snowflake',
    fields: [
      { name: 'account', label: 'Account Identifier', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'password', label: 'Password', type: 'password', required: true },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'warehouse', label: 'Warehouse', type: 'text', required: true },
      { name: 'schema', label: 'Schema', type: 'text', default: 'PUBLIC' },
    ],
    advanced: [
      { name: 'role', label: 'Role', type: 'text' },
    ],
  },
  // Cloud Storage
  google_drive: {
    name: 'Google Drive',
    oauth: true,
    fields: [
      { name: 'folder_id', label: 'Folder ID (optional)', type: 'text', helpText: 'Leave empty to access entire drive' },
    ],
  },
  dropbox: {
    name: 'Dropbox',
    oauth: true,
    fields: [
      { name: 'root_path', label: 'Root Path', type: 'text', default: '/', helpText: 'Start path for file browsing' },
    ],
  },
  s3: {
    name: 'Amazon S3',
    fields: [
      { name: 'bucket', label: 'Bucket Name', type: 'text', required: true },
      { name: 'region', label: 'Region', type: 'select', required: true, options: [
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        'eu-west-1', 'eu-west-2', 'eu-central-1',
        'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2',
      ], default: 'us-east-1' },
      { name: 'access_key_id', label: 'Access Key ID', type: 'text', required: true },
      { name: 'secret_access_key', label: 'Secret Access Key', type: 'password', required: true },
    ],
    advanced: [
      { name: 'prefix', label: 'Key Prefix', type: 'text', helpText: 'Filter objects by prefix' },
      { name: 'endpoint_url', label: 'Custom Endpoint URL', type: 'text', helpText: 'For S3-compatible services' },
    ],
  },
  azure_blob: {
    name: 'Azure Blob Storage',
    fields: [
      { name: 'account_name', label: 'Storage Account Name', type: 'text', required: true },
      { name: 'container', label: 'Container Name', type: 'text', required: true },
      { name: 'connection_string', label: 'Connection String', type: 'password', required: true },
    ],
    advanced: [
      { name: 'prefix', label: 'Blob Prefix', type: 'text' },
    ],
  },
  onedrive: {
    name: 'OneDrive',
    oauth: true,
    fields: [
      { name: 'drive_id', label: 'Drive ID (optional)', type: 'text', helpText: 'Leave empty for default drive' },
    ],
  },
}

/**
 * Get connector field configuration
 */
export function getConnectorConfig(connectorType) {
  return CONNECTOR_FIELDS[connectorType] || null
}

/**
 * Validate connection form values
 */
export function validateConnectionForm(connectorType, values) {
  const config = CONNECTOR_FIELDS[connectorType]
  if (!config) return { valid: true, errors: {} }

  const errors = {}
  const fields = [...(config.fields || []), ...(config.advanced || [])]

  fields.forEach((field) => {
    if (field.required && !values[field.name]) {
      errors[field.name] = `${field.label} is required`
    }
  })

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  }
}
