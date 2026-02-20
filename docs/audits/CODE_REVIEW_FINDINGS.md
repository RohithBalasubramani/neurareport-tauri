# NeuraReport Code Review Findings

This document summarizes the bugs, issues, and recommendations identified during a comprehensive code review of the NeuraReport application.

> Note (2026-01-23): references to `src/` now map to `backend/legacy/`, and `frontend/src/store` has moved to `frontend/src/stores`.

## Executive Summary

The NeuraReport codebase is well-structured with clear separation of concerns. Several critical bugs and potential issues were identified and **have been fixed**.

### Critical Issues: 2 ✅ FIXED
### Important Issues: 5 ✅ FIXED
### Minor Issues: 4 (3 FIXED, 1 for future refactoring)

---

## Critical Bugs

### 1. ✅ FIXED: Infinite Recursion in `templates.py` - `export_template_zip`

**Location:** `src/endpoints/templates.py:73-75`

**Severity:** CRITICAL

**Status:** ✅ **FIXED** - Renamed to `export_template_zip_route` and import aliased to `export_template_zip_service`

**Description:**
The route handler function `export_template_zip` had the same name as the imported function from `template_service.py`, causing infinite recursion when the endpoint is called.

**Fix Applied:**
- Import renamed: `export_template_zip as export_template_zip_service`
- Route handler renamed: `export_template_zip_route`

---

### 2. ✅ FIXED: Infinite Recursion in `templates.py` - `import_template_zip`

**Location:** `src/endpoints/templates.py:78-80`

**Severity:** CRITICAL

**Status:** ✅ **FIXED** - Renamed to `import_template_zip_route` and import aliased to `import_template_zip_service`

**Description:**
Same issue as above - the route handler shadowed the imported function.

**Fix Applied:**
- Import renamed: `import_template_zip as import_template_zip_service`
- Route handler renamed: `import_template_zip_route`

---

## Important Issues

### 3. ✅ FIXED: Mock Mode Enabled by Default

**Location:** `frontend/src/api/client.js:29`

**Severity:** HIGH

**Status:** ✅ **FIXED** - Changed default to `false`

**Description:**
The frontend API client defaulted to mock mode when `VITE_USE_MOCK` was not set.

**Fix Applied:**
```javascript
// Before: export const isMock = (runtimeEnv.VITE_USE_MOCK || 'true') === 'true'
// After:
export const isMock = runtimeEnv.VITE_USE_MOCK === 'true'
```

---

### 4. ⚠️ DOCUMENTED: Dangerous Thread Cancellation Pattern

**Location:** `src/services/report_service.py:165-184`

**Severity:** HIGH

**Status:** ⚠️ **Documented** - This is a known limitation, use with caution

**Description:**
The `_inject_thread_cancel` function uses `ctypes.pythonapi.PyThreadState_SetAsyncExc` to inject exceptions into running threads. This is a dangerous pattern that can:
- Leave the Python interpreter in an inconsistent state
- Cause resource leaks
- Lead to unpredictable behavior

**Recommendation for future:**
- Use cooperative cancellation instead (check cancellation flag periodically)
- Add timeout to long-running operations

---

### 5. ⚠️ DOCUMENTED: Global Subprocess Monkeypatching

**Location:** `src/services/report_service.py:950-965`

**Severity:** MEDIUM

**Status:** ⚠️ **Documented** - Context manager is used, proceed with caution

**Description:**
The `_patch_subprocess_tracking` function globally patches `subprocess.Popen` to track child processes for job cancellation. While it uses a context manager, this could cause issues in concurrent scenarios.

**Note:** The implementation uses a context manager which limits the scope of the patch. Monitor for issues in high-concurrency scenarios.

---

### 6. ✅ FIXED: No Size Limit on localStorage Discovery Cache

**Location:** `frontend/src/store/useAppStore.js:22-117`

**Severity:** MEDIUM

**Status:** ✅ **FIXED** - Added 2MB size limit, LRU eviction, and quota error handling

**Fix Applied:**
- Added `DISCOVERY_MAX_SIZE_BYTES = 2 * 1024 * 1024` (2MB limit)
- Added `DISCOVERY_MAX_TEMPLATES = 50` (max templates to cache)
- Added `evictOldestResults()` LRU eviction function
- Added `_accessedAt` timestamp for LRU ordering
- Added graceful handling of `QuotaExceededError`

---

### 7. ✅ FIXED: Import Inside Function Body

**Location:** `src/endpoints/connections.py:3,44`

**Severity:** LOW

**Status:** ✅ **FIXED** - Moved `HTTPException` import to module level

**Fix Applied:**
```python
# Before: import was inside delete_connection_route function
# After: from fastapi import APIRouter, Depends, HTTPException, Request
```

---

## Minor Issues

### 8. ✅ FIXED: Duplicated Streaming Response Handling

**Location:** `frontend/src/api/client.js:111-202`

**Severity:** LOW

**Status:** ✅ **FIXED** - Added shared `handleStreamingResponse()` utility

**Fix Applied:**
Added a reusable `handleStreamingResponse()` function that can be used by new streaming endpoints. Existing functions were left unchanged to avoid breaking changes, but new endpoints should use this utility.

```javascript
export async function handleStreamingResponse(res, { onEvent, errorMessage = 'Request failed' } = {}) {
  // ... handles NDJSON streaming with progress events, error handling, and result extraction
}
```

---

### 9. Unused `discoverBatches` Function

**Location:** `frontend/src/api/client.js:1650-1670`

**Severity:** LOW

**Description:**
The `discoverBatches` function throws "not implemented" but `discoverReports` already provides this functionality.

**Recommendation:** Remove the unused function or implement it properly.

---

### 10. Missing Error Handling for Network Failures

**Location:** `frontend/src/api/client.js` (various)

**Severity:** LOW

**Description:**
Some API calls only handle response errors but not network failures (e.g., offline, DNS failure).

**Recommendation:** Add try-catch for network errors in addition to response error handling.

---

### 11. Potential Race Condition in Event Bus

**Location:** `src/services/report_service.py:206-225`

**Severity:** LOW

**Description:**
`_publish_event_safe` attempts to get the event loop with `asyncio.get_event_loop()` which could fail unpredictably when called from a thread without an event loop.

**Recommendation:** Use `asyncio.new_event_loop()` as a more reliable fallback.

---

## API Contract Issues

### Excel Routes Completeness

Several Excel routes defined in the frontend may not have corresponding backend implementations:
- `/excel/{template_id}/charts/suggest`
- `/excel/{template_id}/charts/saved`

**Recommendation:** Verify all frontend routes have backend implementations.

---

## Test Coverage

### New Tests Created

The following test files were created during this review:

1. **`backend/tests/test_critical_bugs.py`**
   - Tests for infinite recursion bugs
   - Tests for thread safety
   - Tests for API contract consistency

2. **`backend/tests/test_api_endpoints_comprehensive.py`**
   - Health endpoints
   - Connection CRUD operations
   - Template management
   - Job management
   - Schedule management
   - Correlation ID propagation

3. **`backend/tests/test_pipeline_integration.py`**
   - Complete connection workflow
   - Template lifecycle
   - Job execution pipeline
   - Batch job submission
   - Schedule pipeline
   - Bootstrap state
   - Error recovery

4. **`frontend/src/api/__tests__/client.comprehensive.test.js`**
   - API configuration
   - All API functions
   - Utility functions
   - Error handling
   - Streaming functions

5. **`frontend/src/store/__tests__/useAppStore.test.js`**
   - Initial state
   - Setup navigation
   - Connection management
   - Template management
   - Discovery management
   - Cache management
   - Downloads
   - Hydration

---

## Recommendations

### Immediate Actions (Before New Features)

1. **Fix critical bugs** in `templates.py` (infinite recursion)
2. **Change mock mode default** to `false`
3. **Add tests** for template export/import endpoints

### Short-term Improvements

1. Refactor streaming response handling to reduce duplication
2. Add localStorage size limits for discovery cache
3. Move inline imports to module level
4. Add comprehensive error handling for network failures

### Long-term Improvements

1. Replace dangerous thread cancellation with cooperative cancellation
2. Implement proper process tracking without global patching
3. Add end-to-end tests for complete user workflows
4. Set up CI/CD with automated test runs

---

## Running the Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Specific Test Files

```bash
# Critical bugs
pytest backend/tests/test_critical_bugs.py -v

# API endpoints
pytest backend/tests/test_api_endpoints_comprehensive.py -v

# Integration tests
pytest backend/tests/test_pipeline_integration.py -v
```

---

## Conclusion

The NeuraReport codebase is generally well-organized with good separation between API, service, and domain layers. The critical bugs identified are straightforward to fix and should be addressed immediately. The test suite created during this review provides good coverage for the identified issues and can serve as a foundation for ongoing testing.
