/**
 * Cross-page data flow type definitions.
 *
 * OutputType   – what kind of data a feature produced
 * TransferAction – what the consumer should do with the data
 * FeatureKey   – stable identifier for each feature
 * FEATURE_ACCEPTS – declarative map: which features accept which output types
 * FEATURE_ROUTES  – route path for each feature
 * FEATURE_LABELS  – human-readable label for each feature
 */

export const OutputType = {
  TEXT: 'text',
  RICH_TEXT: 'rich_text',
  TABLE: 'table',
  DOCUMENT: 'document',
  DIAGRAM: 'diagram',
  DATASET: 'dataset',
  REPORT: 'report',
  ANALYSIS: 'analysis',
}

export const TransferAction = {
  OPEN_IN: 'open_in',
  ADD_TO: 'add_to',
  CREATE_FROM: 'create_from',
  CHAT_WITH: 'chat_with',
  ENRICH: 'enrich',
  VISUALIZE: 'visualize',
  SAVE_TO: 'save_to',
}

export const FeatureKey = {
  AGENTS: 'agents',
  DOCQA: 'docqa',
  SYNTHESIS: 'synthesis',
  SUMMARY: 'summary',
  QUERY: 'query',
  VISUALIZATION: 'visualization',
  KNOWLEDGE: 'knowledge',
  ENRICHMENT: 'enrichment',
  FEDERATION: 'federation',
  DOCUMENTS: 'documents',
  SPREADSHEETS: 'spreadsheets',
  DASHBOARDS: 'dashboards',
  WORKFLOWS: 'workflows',
  INGESTION: 'ingestion',
  REPORTS: 'reports',
  DESIGN: 'design',
  SEARCH: 'search',
}

export const FEATURE_ACCEPTS = {
  [FeatureKey.DOCQA]: [OutputType.TEXT, OutputType.RICH_TEXT, OutputType.DOCUMENT, OutputType.REPORT],
  [FeatureKey.SYNTHESIS]: [OutputType.TEXT, OutputType.RICH_TEXT, OutputType.DOCUMENT, OutputType.REPORT],
  [FeatureKey.DOCUMENTS]: [OutputType.TEXT, OutputType.RICH_TEXT, OutputType.ANALYSIS, OutputType.REPORT],
  [FeatureKey.SPREADSHEETS]: [OutputType.TABLE, OutputType.DATASET],
  [FeatureKey.DASHBOARDS]: [OutputType.TABLE, OutputType.DIAGRAM, OutputType.DATASET],
  [FeatureKey.KNOWLEDGE]: [OutputType.TEXT, OutputType.RICH_TEXT, OutputType.DOCUMENT, OutputType.ANALYSIS, OutputType.REPORT],
  [FeatureKey.ENRICHMENT]: [OutputType.TABLE, OutputType.DATASET],
  [FeatureKey.VISUALIZATION]: [OutputType.TABLE, OutputType.DATASET, OutputType.TEXT],
  [FeatureKey.SUMMARY]: [OutputType.TEXT, OutputType.RICH_TEXT, OutputType.DOCUMENT],
  [FeatureKey.REPORTS]: [OutputType.TABLE, OutputType.DATASET, OutputType.ANALYSIS],
}

export const FEATURE_ROUTES = {
  [FeatureKey.AGENTS]: '/agents',
  [FeatureKey.DOCQA]: '/docqa',
  [FeatureKey.SYNTHESIS]: '/synthesis',
  [FeatureKey.SUMMARY]: '/summary',
  [FeatureKey.QUERY]: '/query',
  [FeatureKey.VISUALIZATION]: '/visualization',
  [FeatureKey.KNOWLEDGE]: '/knowledge',
  [FeatureKey.ENRICHMENT]: '/enrichment',
  [FeatureKey.FEDERATION]: '/federation',
  [FeatureKey.DOCUMENTS]: '/documents',
  [FeatureKey.SPREADSHEETS]: '/spreadsheets',
  [FeatureKey.DASHBOARDS]: '/dashboard-builder',
  [FeatureKey.WORKFLOWS]: '/workflows',
  [FeatureKey.INGESTION]: '/ingestion',
  [FeatureKey.REPORTS]: '/reports',
  [FeatureKey.DESIGN]: '/design',
  [FeatureKey.SEARCH]: '/search',
}

export const FEATURE_LABELS = {
  [FeatureKey.AGENTS]: 'AI Agents',
  [FeatureKey.DOCQA]: 'Chat with Docs',
  [FeatureKey.SYNTHESIS]: 'Synthesis',
  [FeatureKey.SUMMARY]: 'Summary',
  [FeatureKey.QUERY]: 'Query Builder',
  [FeatureKey.VISUALIZATION]: 'Visualization',
  [FeatureKey.KNOWLEDGE]: 'Knowledge Base',
  [FeatureKey.ENRICHMENT]: 'Enrichment',
  [FeatureKey.FEDERATION]: 'Federation',
  [FeatureKey.DOCUMENTS]: 'Documents',
  [FeatureKey.SPREADSHEETS]: 'Spreadsheets',
  [FeatureKey.DASHBOARDS]: 'Dashboard Builder',
  [FeatureKey.WORKFLOWS]: 'Workflows',
  [FeatureKey.INGESTION]: 'Ingestion',
  [FeatureKey.REPORTS]: 'Reports',
  [FeatureKey.DESIGN]: 'Design',
  [FeatureKey.SEARCH]: 'Search',
}

/**
 * For each target feature, which transfer actions make sense.
 * Used by SendToMenu to build contextual action labels.
 */
export const FEATURE_ACTIONS = {
  [FeatureKey.DOCQA]: { action: TransferAction.CHAT_WITH, label: 'Chat with this' },
  [FeatureKey.SYNTHESIS]: { action: TransferAction.ADD_TO, label: 'Add to Synthesis' },
  [FeatureKey.DOCUMENTS]: { action: TransferAction.CREATE_FROM, label: 'Create Document' },
  [FeatureKey.SPREADSHEETS]: { action: TransferAction.OPEN_IN, label: 'Open in Spreadsheet' },
  [FeatureKey.DASHBOARDS]: { action: TransferAction.ADD_TO, label: 'Add to Dashboard' },
  [FeatureKey.KNOWLEDGE]: { action: TransferAction.SAVE_TO, label: 'Save to Knowledge' },
  [FeatureKey.ENRICHMENT]: { action: TransferAction.ENRICH, label: 'Enrich Data' },
  [FeatureKey.VISUALIZATION]: { action: TransferAction.VISUALIZE, label: 'Visualize' },
  [FeatureKey.SUMMARY]: { action: TransferAction.OPEN_IN, label: 'Summarize' },
  [FeatureKey.REPORTS]: { action: TransferAction.CREATE_FROM, label: 'Generate Report' },
}
