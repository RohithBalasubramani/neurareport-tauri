# JobsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**cancelJobRouteApiV1JobsJobIdCancelPost**](#canceljobrouteapiv1jobsjobidcancelpost) | **POST** /api/v1/jobs/{job_id}/cancel | Cancel Job Route|
|[**deleteFromDlqRouteApiV1JobsDeadLetterJobIdDelete**](#deletefromdlqrouteapiv1jobsdeadletterjobiddelete) | **DELETE** /api/v1/jobs/dead-letter/{job_id} | Delete From Dlq Route|
|[**getDeadLetterJobRouteApiV1JobsDeadLetterJobIdGet**](#getdeadletterjobrouteapiv1jobsdeadletterjobidget) | **GET** /api/v1/jobs/dead-letter/{job_id} | Get Dead Letter Job Route|
|[**getJobRouteApiV1JobsJobIdGet**](#getjobrouteapiv1jobsjobidget) | **GET** /api/v1/jobs/{job_id} | Get Job Route|
|[**listActiveJobsRouteApiV1JobsActiveGet**](#listactivejobsrouteapiv1jobsactiveget) | **GET** /api/v1/jobs/active | List Active Jobs Route|
|[**listDeadLetterJobsRouteApiV1JobsDeadLetterGet**](#listdeadletterjobsrouteapiv1jobsdeadletterget) | **GET** /api/v1/jobs/dead-letter | List Dead Letter Jobs Route|
|[**listJobsRouteApiV1JobsGet**](#listjobsrouteapiv1jobsget) | **GET** /api/v1/jobs | List Jobs Route|
|[**requeueFromDlqRouteApiV1JobsDeadLetterJobIdRequeuePost**](#requeuefromdlqrouteapiv1jobsdeadletterjobidrequeuepost) | **POST** /api/v1/jobs/dead-letter/{job_id}/requeue | Requeue From Dlq Route|
|[**retryJobRouteApiV1JobsJobIdRetryPost**](#retryjobrouteapiv1jobsjobidretrypost) | **POST** /api/v1/jobs/{job_id}/retry | Retry Job Route|
|[**runReportJobApiV1JobsRunReportPost**](#runreportjobapiv1jobsrunreportpost) | **POST** /api/v1/jobs/run-report | Run Report Job|

# **cancelJobRouteApiV1JobsJobIdCancelPost**
> any cancelJobRouteApiV1JobsJobIdCancelPost()

Cancel a running job.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobId: string; // (default to undefined)
let force: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelJobRouteApiV1JobsJobIdCancelPost(
    jobId,
    force,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|
| **force** | [**boolean**] |  | (optional) defaults to false|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteFromDlqRouteApiV1JobsDeadLetterJobIdDelete**
> any deleteFromDlqRouteApiV1JobsDeadLetterJobIdDelete()

Permanently delete a job from the Dead Letter Queue.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteFromDlqRouteApiV1JobsDeadLetterJobIdDelete(
    jobId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getDeadLetterJobRouteApiV1JobsDeadLetterJobIdGet**
> any getDeadLetterJobRouteApiV1JobsDeadLetterJobIdGet()

Get a specific job from the Dead Letter Queue.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDeadLetterJobRouteApiV1JobsDeadLetterJobIdGet(
    jobId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getJobRouteApiV1JobsJobIdGet**
> any getJobRouteApiV1JobsJobIdGet()

Get details for a specific job.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getJobRouteApiV1JobsJobIdGet(
    jobId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listActiveJobsRouteApiV1JobsActiveGet**
> any listActiveJobsRouteApiV1JobsActiveGet()

List only active (non-completed) jobs.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let limit: number; // (optional) (default to 20)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listActiveJobsRouteApiV1JobsActiveGet(
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 20|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listDeadLetterJobsRouteApiV1JobsDeadLetterGet**
> any listDeadLetterJobsRouteApiV1JobsDeadLetterGet()

List jobs in the Dead Letter Queue.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let limit: number; // (optional) (default to 50)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDeadLetterJobsRouteApiV1JobsDeadLetterGet(
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listJobsRouteApiV1JobsGet**
> any listJobsRouteApiV1JobsGet()

List jobs with optional filtering by status and type.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let status: Array<string>; // (optional) (default to undefined)
let type: Array<string>; // (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let activeOnly: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listJobsRouteApiV1JobsGet(
    status,
    type,
    limit,
    activeOnly,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **status** | **Array&lt;string&gt;** |  | (optional) defaults to undefined|
| **type** | **Array&lt;string&gt;** |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **activeOnly** | [**boolean**] |  | (optional) defaults to false|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **requeueFromDlqRouteApiV1JobsDeadLetterJobIdRequeuePost**
> any requeueFromDlqRouteApiV1JobsDeadLetterJobIdRequeuePost()

Requeue a job from the Dead Letter Queue.  Creates a new job with reset retry count and state.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.requeueFromDlqRouteApiV1JobsDeadLetterJobIdRequeuePost(
    jobId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retryJobRouteApiV1JobsJobIdRetryPost**
> any retryJobRouteApiV1JobsJobIdRetryPost()

Retry a failed job by re-queuing it with the same parameters.  Only jobs with status \'failed\' can be retried.

### Example

```typescript
import {
    JobsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.retryJobRouteApiV1JobsJobIdRetryPost(
    jobId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **runReportJobApiV1JobsRunReportPost**
> any runReportJobApiV1JobsRunReportPost(payload)

Queue a report generation job (compatibility alias for `/reports/jobs/run-report`).

### Example

```typescript
import {
    JobsApi,
    Configuration,
    Payload
} from './api';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let payload: Payload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runReportJobApiV1JobsRunReportPost(
    payload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **payload** | **Payload**|  | |
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

