# SchedulesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createReportScheduleApiV1ReportsSchedulesPost**](#createreportscheduleapiv1reportsschedulespost) | **POST** /api/v1/reports/schedules | Create Report Schedule|
|[**deleteReportScheduleApiV1ReportsSchedulesScheduleIdDelete**](#deletereportscheduleapiv1reportsschedulesscheduleiddelete) | **DELETE** /api/v1/reports/schedules/{schedule_id} | Delete Report Schedule|
|[**getReportScheduleApiV1ReportsSchedulesScheduleIdGet**](#getreportscheduleapiv1reportsschedulesscheduleidget) | **GET** /api/v1/reports/schedules/{schedule_id} | Get Report Schedule|
|[**listReportSchedulesApiV1ReportsSchedulesGet**](#listreportschedulesapiv1reportsschedulesget) | **GET** /api/v1/reports/schedules | List Report Schedules|
|[**pauseScheduleApiV1ReportsSchedulesScheduleIdPausePost**](#pausescheduleapiv1reportsschedulesscheduleidpausepost) | **POST** /api/v1/reports/schedules/{schedule_id}/pause | Pause Schedule|
|[**resumeScheduleApiV1ReportsSchedulesScheduleIdResumePost**](#resumescheduleapiv1reportsschedulesscheduleidresumepost) | **POST** /api/v1/reports/schedules/{schedule_id}/resume | Resume Schedule|
|[**triggerScheduleApiV1ReportsSchedulesScheduleIdTriggerPost**](#triggerscheduleapiv1reportsschedulesscheduleidtriggerpost) | **POST** /api/v1/reports/schedules/{schedule_id}/trigger | Trigger Schedule|
|[**updateReportScheduleApiV1ReportsSchedulesScheduleIdPut**](#updatereportscheduleapiv1reportsschedulesscheduleidput) | **PUT** /api/v1/reports/schedules/{schedule_id} | Update Report Schedule|

# **createReportScheduleApiV1ReportsSchedulesPost**
> any createReportScheduleApiV1ReportsSchedulesPost(scheduleCreatePayload)

Create a new report schedule.

### Example

```typescript
import {
    SchedulesApi,
    Configuration,
    ScheduleCreatePayload
} from './api';

const configuration = new Configuration();
const apiInstance = new SchedulesApi(configuration);

let scheduleCreatePayload: ScheduleCreatePayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createReportScheduleApiV1ReportsSchedulesPost(
    scheduleCreatePayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scheduleCreatePayload** | **ScheduleCreatePayload**|  | |
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

# **deleteReportScheduleApiV1ReportsSchedulesScheduleIdDelete**
> any deleteReportScheduleApiV1ReportsSchedulesScheduleIdDelete()

Delete a report schedule.

### Example

```typescript
import {
    SchedulesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SchedulesApi(configuration);

let scheduleId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteReportScheduleApiV1ReportsSchedulesScheduleIdDelete(
    scheduleId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scheduleId** | [**string**] |  | defaults to undefined|
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

# **getReportScheduleApiV1ReportsSchedulesScheduleIdGet**
> any getReportScheduleApiV1ReportsSchedulesScheduleIdGet()

Get a specific schedule by ID.

### Example

```typescript
import {
    SchedulesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SchedulesApi(configuration);

let scheduleId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getReportScheduleApiV1ReportsSchedulesScheduleIdGet(
    scheduleId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scheduleId** | [**string**] |  | defaults to undefined|
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

# **listReportSchedulesApiV1ReportsSchedulesGet**
> any listReportSchedulesApiV1ReportsSchedulesGet()

List all report schedules.

### Example

```typescript
import {
    SchedulesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SchedulesApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listReportSchedulesApiV1ReportsSchedulesGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
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

# **pauseScheduleApiV1ReportsSchedulesScheduleIdPausePost**
> any pauseScheduleApiV1ReportsSchedulesScheduleIdPausePost()

Pause a schedule (set active to false).

### Example

```typescript
import {
    SchedulesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SchedulesApi(configuration);

let scheduleId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.pauseScheduleApiV1ReportsSchedulesScheduleIdPausePost(
    scheduleId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scheduleId** | [**string**] |  | defaults to undefined|
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

# **resumeScheduleApiV1ReportsSchedulesScheduleIdResumePost**
> any resumeScheduleApiV1ReportsSchedulesScheduleIdResumePost()

Resume a paused schedule (set active to true).

### Example

```typescript
import {
    SchedulesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SchedulesApi(configuration);

let scheduleId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resumeScheduleApiV1ReportsSchedulesScheduleIdResumePost(
    scheduleId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scheduleId** | [**string**] |  | defaults to undefined|
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

# **triggerScheduleApiV1ReportsSchedulesScheduleIdTriggerPost**
> any triggerScheduleApiV1ReportsSchedulesScheduleIdTriggerPost()

Manually trigger a scheduled report to run immediately.  This creates a job and queues it for execution without waiting for the next scheduled run. The actual report generation happens asynchronously.

### Example

```typescript
import {
    SchedulesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SchedulesApi(configuration);

let scheduleId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.triggerScheduleApiV1ReportsSchedulesScheduleIdTriggerPost(
    scheduleId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scheduleId** | [**string**] |  | defaults to undefined|
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

# **updateReportScheduleApiV1ReportsSchedulesScheduleIdPut**
> any updateReportScheduleApiV1ReportsSchedulesScheduleIdPut(scheduleUpdatePayload)

Update an existing report schedule.

### Example

```typescript
import {
    SchedulesApi,
    Configuration,
    ScheduleUpdatePayload
} from './api';

const configuration = new Configuration();
const apiInstance = new SchedulesApi(configuration);

let scheduleId: string; // (default to undefined)
let scheduleUpdatePayload: ScheduleUpdatePayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateReportScheduleApiV1ReportsSchedulesScheduleIdPut(
    scheduleId,
    scheduleUpdatePayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scheduleUpdatePayload** | **ScheduleUpdatePayload**|  | |
| **scheduleId** | [**string**] |  | defaults to undefined|
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

