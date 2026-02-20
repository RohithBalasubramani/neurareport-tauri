# ChartsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**analyzeForChartsApiV1ChartsAnalyzePost**](#analyzeforchartsapiv1chartsanalyzepost) | **POST** /api/v1/charts/analyze | Analyze For Charts|
|[**generateChartConfigApiV1ChartsGeneratePost**](#generatechartconfigapiv1chartsgeneratepost) | **POST** /api/v1/charts/generate | Generate Chart Config|

# **analyzeForChartsApiV1ChartsAnalyzePost**
> any analyzeForChartsApiV1ChartsAnalyzePost(chartAnalyzeRequest)

Analyze data and suggest appropriate chart visualizations.

### Example

```typescript
import {
    ChartsApi,
    Configuration,
    ChartAnalyzeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ChartsApi(configuration);

let chartAnalyzeRequest: ChartAnalyzeRequest; //
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.analyzeForChartsApiV1ChartsAnalyzePost(
    chartAnalyzeRequest,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chartAnalyzeRequest** | **ChartAnalyzeRequest**|  | |
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

# **generateChartConfigApiV1ChartsGeneratePost**
> any generateChartConfigApiV1ChartsGeneratePost(chartGenerateRequest)

Generate a chart configuration.

### Example

```typescript
import {
    ChartsApi,
    Configuration,
    ChartGenerateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ChartsApi(configuration);

let chartGenerateRequest: ChartGenerateRequest; //
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateChartConfigApiV1ChartsGeneratePost(
    chartGenerateRequest,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chartGenerateRequest** | **ChartGenerateRequest**|  | |
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

