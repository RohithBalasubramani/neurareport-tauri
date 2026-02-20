# SummaryApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**generateSummaryApiV1SummaryGeneratePost**](#generatesummaryapiv1summarygeneratepost) | **POST** /api/v1/summary/generate | Generate Summary|
|[**getReportSummaryApiV1SummaryReportsReportIdGet**](#getreportsummaryapiv1summaryreportsreportidget) | **GET** /api/v1/summary/reports/{report_id} | Get Report Summary|

# **generateSummaryApiV1SummaryGeneratePost**
> any generateSummaryApiV1SummaryGeneratePost(summaryRequest)

Generate an executive summary from content.

### Example

```typescript
import {
    SummaryApi,
    Configuration,
    SummaryRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SummaryApi(configuration);

let summaryRequest: SummaryRequest; //
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateSummaryApiV1SummaryGeneratePost(
    summaryRequest,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **summaryRequest** | **SummaryRequest**|  | |
| **background** | [**boolean**] |  | (optional) defaults to false|
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

# **getReportSummaryApiV1SummaryReportsReportIdGet**
> any getReportSummaryApiV1SummaryReportsReportIdGet()

Generate summary for a specific report.

### Example

```typescript
import {
    SummaryApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SummaryApi(configuration);

let reportId: string; // (default to undefined)
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getReportSummaryApiV1SummaryReportsReportIdGet(
    reportId,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **reportId** | [**string**] |  | defaults to undefined|
| **background** | [**boolean**] |  | (optional) defaults to false|
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

