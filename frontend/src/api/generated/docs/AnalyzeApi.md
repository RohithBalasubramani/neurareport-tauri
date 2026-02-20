# AnalyzeApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**extractDocumentApiV1AnalyzeExtractPost**](#extractdocumentapiv1analyzeextractpost) | **POST** /api/v1/analyze/extract | Extract Document|
|[**getAnalysisRawDataApiV1AnalyzeAnalysisIdDataGet**](#getanalysisrawdataapiv1analyzeanalysisiddataget) | **GET** /api/v1/analyze/{analysis_id}/data | Get Analysis Raw Data|
|[**getAnalysisResultApiV1AnalyzeAnalysisIdGet**](#getanalysisresultapiv1analyzeanalysisidget) | **GET** /api/v1/analyze/{analysis_id} | Get Analysis Result|
|[**suggestChartsApiV1AnalyzeAnalysisIdChartsSuggestPost**](#suggestchartsapiv1analyzeanalysisidchartssuggestpost) | **POST** /api/v1/analyze/{analysis_id}/charts/suggest | Suggest Charts|
|[**uploadAndAnalyzeApiV1AnalyzeUploadPost**](#uploadandanalyzeapiv1analyzeuploadpost) | **POST** /api/v1/analyze/upload | Upload And Analyze|

# **extractDocumentApiV1AnalyzeExtractPost**
> any extractDocumentApiV1AnalyzeExtractPost()

Quickly extract raw tables and text without full AI analysis.

### Example

```typescript
import {
    AnalyzeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyzeApi(configuration);

let file: File; // (default to undefined)
let tableLimit: number; // (optional) (default to 50)
let tableOffset: number; // (optional) (default to 0)
let textLimit: number; // (optional) (default to 50000)
let includeText: boolean; // (optional) (default to true)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.extractDocumentApiV1AnalyzeExtractPost(
    file,
    tableLimit,
    tableOffset,
    textLimit,
    includeText,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **tableLimit** | [**number**] |  | (optional) defaults to 50|
| **tableOffset** | [**number**] |  | (optional) defaults to 0|
| **textLimit** | [**number**] |  | (optional) defaults to 50000|
| **includeText** | [**boolean**] |  | (optional) defaults to true|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAnalysisRawDataApiV1AnalyzeAnalysisIdDataGet**
> any getAnalysisRawDataApiV1AnalyzeAnalysisIdDataGet()

Get raw data from an analysis for charting.

### Example

```typescript
import {
    AnalyzeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyzeApi(configuration);

let analysisId: string; // (default to undefined)
let limit: number; // (optional) (default to 500)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAnalysisRawDataApiV1AnalyzeAnalysisIdDataGet(
    analysisId,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **analysisId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 500|
| **offset** | [**number**] |  | (optional) defaults to 0|
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

# **getAnalysisResultApiV1AnalyzeAnalysisIdGet**
> any getAnalysisResultApiV1AnalyzeAnalysisIdGet()

Get a previously computed analysis result.

### Example

```typescript
import {
    AnalyzeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyzeApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAnalysisResultApiV1AnalyzeAnalysisIdGet(
    analysisId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **analysisId** | [**string**] |  | defaults to undefined|
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

# **suggestChartsApiV1AnalyzeAnalysisIdChartsSuggestPost**
> any suggestChartsApiV1AnalyzeAnalysisIdChartsSuggestPost(analysisSuggestChartsPayload)

Generate additional chart suggestions for an existing analysis.

### Example

```typescript
import {
    AnalyzeApi,
    Configuration,
    AnalysisSuggestChartsPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyzeApi(configuration);

let analysisId: string; // (default to undefined)
let analysisSuggestChartsPayload: AnalysisSuggestChartsPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestChartsApiV1AnalyzeAnalysisIdChartsSuggestPost(
    analysisId,
    analysisSuggestChartsPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **analysisSuggestChartsPayload** | **AnalysisSuggestChartsPayload**|  | |
| **analysisId** | [**string**] |  | defaults to undefined|
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

# **uploadAndAnalyzeApiV1AnalyzeUploadPost**
> any uploadAndAnalyzeApiV1AnalyzeUploadPost()

Upload a document (PDF or Excel) and analyze it with AI.  Returns a streaming NDJSON response with progress updates and final results. Use background=true to queue the analysis as a job.  Events: - stage: Progress update with stage name and percentage - error: Error occurred, includes detail message - result: Final analysis result

### Example

```typescript
import {
    AnalyzeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyzeApi(configuration);

let file: File; // (default to undefined)
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)
let connectionId: string; // (optional) (default to undefined)
let templateId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.uploadAndAnalyzeApiV1AnalyzeUploadPost(
    file,
    background,
    xApiKey,
    connectionId,
    templateId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **background** | [**boolean**] |  | (optional) defaults to false|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|
| **templateId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

