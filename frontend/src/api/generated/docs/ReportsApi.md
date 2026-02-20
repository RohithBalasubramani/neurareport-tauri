# ReportsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**discoverReportsApiV1ReportsDiscoverPost**](#discoverreportsapiv1reportsdiscoverpost) | **POST** /api/v1/reports/discover | Discover Reports|
|[**enqueueReportJobApiV1ReportsJobsRunReportPost**](#enqueuereportjobapiv1reportsjobsrunreportpost) | **POST** /api/v1/reports/jobs/run-report | Enqueue Report Job|
|[**getReportRunRouteApiV1ReportsRunsRunIdGet**](#getreportrunrouteapiv1reportsrunsrunidget) | **GET** /api/v1/reports/runs/{run_id} | Get Report Run Route|
|[**listReportRunsRouteApiV1ReportsRunsGet**](#listreportrunsrouteapiv1reportsrunsget) | **GET** /api/v1/reports/runs | List Report Runs Route|
|[**runReportApiV1ReportsRunPost**](#runreportapiv1reportsrunpost) | **POST** /api/v1/reports/run | Run Report|

# **discoverReportsApiV1ReportsDiscoverPost**
> any discoverReportsApiV1ReportsDiscoverPost(discoverPayload)

Discover available batches for report generation.

### Example

```typescript
import {
    ReportsApi,
    Configuration,
    DiscoverPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let discoverPayload: DiscoverPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.discoverReportsApiV1ReportsDiscoverPost(
    discoverPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **discoverPayload** | **DiscoverPayload**|  | |
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

# **enqueueReportJobApiV1ReportsJobsRunReportPost**
> any enqueueReportJobApiV1ReportsJobsRunReportPost(payload)

Queue a PDF report job for async generation.

### Example

```typescript
import {
    ReportsApi,
    Configuration,
    Payload
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let payload: Payload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.enqueueReportJobApiV1ReportsJobsRunReportPost(
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

# **getReportRunRouteApiV1ReportsRunsRunIdGet**
> any getReportRunRouteApiV1ReportsRunsRunIdGet()

Get a specific report run by ID.

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let runId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getReportRunRouteApiV1ReportsRunsRunIdGet(
    runId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **runId** | [**string**] |  | defaults to undefined|
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

# **listReportRunsRouteApiV1ReportsRunsGet**
> any listReportRunsRouteApiV1ReportsRunsGet()

List report generation runs with optional filtering.

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let templateId: string; // (optional) (default to undefined)
let connectionId: string; // (optional) (default to undefined)
let scheduleId: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listReportRunsRouteApiV1ReportsRunsGet(
    templateId,
    connectionId,
    scheduleId,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | (optional) defaults to undefined|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|
| **scheduleId** | [**string**] |  | (optional) defaults to undefined|
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

# **runReportApiV1ReportsRunPost**
> any runReportApiV1ReportsRunPost(runPayload)

Run a PDF report synchronously.

### Example

```typescript
import {
    ReportsApi,
    Configuration,
    RunPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let runPayload: RunPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runReportApiV1ReportsRunPost(
    runPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **runPayload** | **RunPayload**|  | |
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

