/**
 * Background Operations Constants
 */

// ============================================================================
// BACKGROUND OPERATION TYPES
// ============================================================================

export const BackgroundOperationType = {
  // User-initiated background tasks
  REPORT_GENERATION: 'report_generation',
  DOCUMENT_PROCESSING: 'document_processing',
  DATA_EXPORT: 'data_export',
  BATCH_OPERATION: 'batch_operation',

  // Scheduled tasks
  SCHEDULED_REPORT: 'scheduled_report',
  DATA_SYNC: 'data_sync',
  CLEANUP: 'cleanup',

  // System tasks (visible but not user-cancelable)
  CACHE_REFRESH: 'cache_refresh',
  INDEX_REBUILD: 'index_rebuild',
  HEALTH_CHECK: 'health_check',
}

export const BackgroundOperationStatus = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
}
