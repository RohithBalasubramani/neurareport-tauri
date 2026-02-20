# AuditApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**recordIntentApiV1AuditIntentPost**](#recordintentapiv1auditintentpost) | **POST** /api/v1/audit/intent | Record Intent|
|[**recordIntentApiV1AuditIntentPost_0**](#recordintentapiv1auditintentpost_0) | **POST** /api/v1/audit/intent | Record Intent|
|[**updateIntentApiV1AuditIntentIdPatch**](#updateintentapiv1auditintentidpatch) | **PATCH** /api/v1/audit/intent/{id} | Update Intent|
|[**updateIntentApiV1AuditIntentIdPatch_0**](#updateintentapiv1auditintentidpatch_0) | **PATCH** /api/v1/audit/intent/{id} | Update Intent|

# **recordIntentApiV1AuditIntentPost**
> any recordIntentApiV1AuditIntentPost(recordIntentRequest)

Record a user intent for audit trail.  Accepts idempotency keys via headers to prevent duplicate recordings.

### Example

```typescript
import {
    AuditApi,
    Configuration,
    RecordIntentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuditApi(configuration);

let recordIntentRequest: RecordIntentRequest; //
let xIdempotencyKey: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.recordIntentApiV1AuditIntentPost(
    recordIntentRequest,
    xIdempotencyKey,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **recordIntentRequest** | **RecordIntentRequest**|  | |
| **xIdempotencyKey** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **recordIntentApiV1AuditIntentPost_0**
> any recordIntentApiV1AuditIntentPost_0(recordIntentRequest)

Record a user intent for audit trail.  Accepts idempotency keys via headers to prevent duplicate recordings.

### Example

```typescript
import {
    AuditApi,
    Configuration,
    RecordIntentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuditApi(configuration);

let recordIntentRequest: RecordIntentRequest; //
let xIdempotencyKey: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.recordIntentApiV1AuditIntentPost_0(
    recordIntentRequest,
    xIdempotencyKey,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **recordIntentRequest** | **RecordIntentRequest**|  | |
| **xIdempotencyKey** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateIntentApiV1AuditIntentIdPatch**
> any updateIntentApiV1AuditIntentIdPatch(updateIntentRequest)

Update an intent with its outcome (completed, failed, cancelled).

### Example

```typescript
import {
    AuditApi,
    Configuration,
    UpdateIntentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuditApi(configuration);

let id: string; // (default to undefined)
let updateIntentRequest: UpdateIntentRequest; //
let xIdempotencyKey: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateIntentApiV1AuditIntentIdPatch(
    id,
    updateIntentRequest,
    xIdempotencyKey,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateIntentRequest** | **UpdateIntentRequest**|  | |
| **id** | [**string**] |  | defaults to undefined|
| **xIdempotencyKey** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateIntentApiV1AuditIntentIdPatch_0**
> any updateIntentApiV1AuditIntentIdPatch_0(updateIntentRequest)

Update an intent with its outcome (completed, failed, cancelled).

### Example

```typescript
import {
    AuditApi,
    Configuration,
    UpdateIntentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuditApi(configuration);

let id: string; // (default to undefined)
let updateIntentRequest: UpdateIntentRequest; //
let xIdempotencyKey: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateIntentApiV1AuditIntentIdPatch_0(
    id,
    updateIntentRequest,
    xIdempotencyKey,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateIntentRequest** | **UpdateIntentRequest**|  | |
| **id** | [**string**] |  | defaults to undefined|
| **xIdempotencyKey** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

