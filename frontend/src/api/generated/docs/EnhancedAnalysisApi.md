# EnhancedAnalysisApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addCommentApiV1AnalyzeV2AnalysisIdCommentsPost**](#addcommentapiv1analyzev2analysisidcommentspost) | **POST** /api/v1/analyze/v2/{analysis_id}/comments | Add Comment|
|[**analyzeDocumentApiV1AnalyzeV2UploadPost**](#analyzedocumentapiv1analyzev2uploadpost) | **POST** /api/v1/analyze/v2/upload | Analyze Document|
|[**askQuestionApiV1AnalyzeV2AnalysisIdAskPost**](#askquestionapiv1analyzev2analysisidaskpost) | **POST** /api/v1/analyze/v2/{analysis_id}/ask | Ask Question|
|[**compareDocumentsApiV1AnalyzeV2ComparePost**](#comparedocumentsapiv1analyzev2comparepost) | **POST** /api/v1/analyze/v2/compare | Compare Documents|
|[**createIntegrationItemApiV1AnalyzeV2IntegrationsIntegrationIdItemsPost**](#createintegrationitemapiv1analyzev2integrationsintegrationiditemspost) | **POST** /api/v1/analyze/v2/integrations/{integration_id}/items | Create Integration Item|
|[**createPipelineApiV1AnalyzeV2PipelinesPost**](#createpipelineapiv1analyzev2pipelinespost) | **POST** /api/v1/analyze/v2/pipelines | Create Pipeline|
|[**createShareLinkApiV1AnalyzeV2AnalysisIdSharePost**](#createsharelinkapiv1analyzev2analysisidsharepost) | **POST** /api/v1/analyze/v2/{analysis_id}/share | Create Share Link|
|[**createTriggerApiV1AnalyzeV2TriggersPost**](#createtriggerapiv1analyzev2triggerspost) | **POST** /api/v1/analyze/v2/triggers | Create Trigger|
|[**executePipelineApiV1AnalyzeV2PipelinesPipelineIdExecutePost**](#executepipelineapiv1analyzev2pipelinespipelineidexecutepost) | **POST** /api/v1/analyze/v2/pipelines/{pipeline_id}/execute | Execute Pipeline|
|[**exportAnalysisApiV1AnalyzeV2AnalysisIdExportPost**](#exportanalysisapiv1analyzev2analysisidexportpost) | **POST** /api/v1/analyze/v2/{analysis_id}/export | Export Analysis|
|[**fetchDataFromSourceApiV1AnalyzeV2SourcesConnectionIdFetchPost**](#fetchdatafromsourceapiv1analyzev2sourcesconnectionidfetchpost) | **POST** /api/v1/analyze/v2/sources/{connection_id}/fetch | Fetch Data From Source|
|[**generateChartsApiV1AnalyzeV2AnalysisIdChartsGeneratePost**](#generatechartsapiv1analyzev2analysisidchartsgeneratepost) | **POST** /api/v1/analyze/v2/{analysis_id}/charts/generate | Generate Charts|
|[**getAnalysisApiV1AnalyzeV2AnalysisIdGet**](#getanalysisapiv1analyzev2analysisidget) | **GET** /api/v1/analyze/v2/{analysis_id} | Get Analysis|
|[**getChartTypesApiV1AnalyzeV2ConfigChartTypesGet**](#getcharttypesapiv1analyzev2configcharttypesget) | **GET** /api/v1/analyze/v2/config/chart-types | Get Chart Types|
|[**getChartsApiV1AnalyzeV2AnalysisIdChartsGet**](#getchartsapiv1analyzev2analysisidchartsget) | **GET** /api/v1/analyze/v2/{analysis_id}/charts | Get Charts|
|[**getCommentsApiV1AnalyzeV2AnalysisIdCommentsGet**](#getcommentsapiv1analyzev2analysisidcommentsget) | **GET** /api/v1/analyze/v2/{analysis_id}/comments | Get Comments|
|[**getDataQualityApiV1AnalyzeV2AnalysisIdQualityGet**](#getdataqualityapiv1analyzev2analysisidqualityget) | **GET** /api/v1/analyze/v2/{analysis_id}/quality | Get Data Quality|
|[**getEntitiesApiV1AnalyzeV2AnalysisIdEntitiesGet**](#getentitiesapiv1analyzev2analysisidentitiesget) | **GET** /api/v1/analyze/v2/{analysis_id}/entities | Get Entities|
|[**getExportFormatsApiV1AnalyzeV2ConfigExportFormatsGet**](#getexportformatsapiv1analyzev2configexportformatsget) | **GET** /api/v1/analyze/v2/config/export-formats | Get Export Formats|
|[**getIndustryOptionsApiV1AnalyzeV2ConfigIndustriesGet**](#getindustryoptionsapiv1analyzev2configindustriesget) | **GET** /api/v1/analyze/v2/config/industries | Get Industry Options|
|[**getInsightsApiV1AnalyzeV2AnalysisIdInsightsGet**](#getinsightsapiv1analyzev2analysisidinsightsget) | **GET** /api/v1/analyze/v2/{analysis_id}/insights | Get Insights|
|[**getMetricsApiV1AnalyzeV2AnalysisIdMetricsGet**](#getmetricsapiv1analyzev2analysisidmetricsget) | **GET** /api/v1/analyze/v2/{analysis_id}/metrics | Get Metrics|
|[**getSharedAnalysisApiV1AnalyzeV2SharedShareIdGet**](#getsharedanalysisapiv1analyzev2sharedshareidget) | **GET** /api/v1/analyze/v2/shared/{share_id} | Get Shared Analysis|
|[**getSuggestedQuestionsApiV1AnalyzeV2AnalysisIdSuggestedQuestionsGet**](#getsuggestedquestionsapiv1analyzev2analysisidsuggestedquestionsget) | **GET** /api/v1/analyze/v2/{analysis_id}/suggested-questions | Get Suggested Questions|
|[**getSummaryApiV1AnalyzeV2AnalysisIdSummaryModeGet**](#getsummaryapiv1analyzev2analysisidsummarymodeget) | **GET** /api/v1/analyze/v2/{analysis_id}/summary/{mode} | Get Summary|
|[**getSummaryModesApiV1AnalyzeV2ConfigSummaryModesGet**](#getsummarymodesapiv1analyzev2configsummarymodesget) | **GET** /api/v1/analyze/v2/config/summary-modes | Get Summary Modes|
|[**getTablesApiV1AnalyzeV2AnalysisIdTablesGet**](#gettablesapiv1analyzev2analysisidtablesget) | **GET** /api/v1/analyze/v2/{analysis_id}/tables | Get Tables|
|[**listDataSourcesApiV1AnalyzeV2SourcesGet**](#listdatasourcesapiv1analyzev2sourcesget) | **GET** /api/v1/analyze/v2/sources | List Data Sources|
|[**listIntegrationsApiV1AnalyzeV2IntegrationsGet**](#listintegrationsapiv1analyzev2integrationsget) | **GET** /api/v1/analyze/v2/integrations | List Integrations|
|[**registerDataSourceApiV1AnalyzeV2SourcesPost**](#registerdatasourceapiv1analyzev2sourcespost) | **POST** /api/v1/analyze/v2/sources | Register Data Source|
|[**registerIntegrationApiV1AnalyzeV2IntegrationsPost**](#registerintegrationapiv1analyzev2integrationspost) | **POST** /api/v1/analyze/v2/integrations | Register Integration|
|[**registerWebhookApiV1AnalyzeV2WebhooksPost**](#registerwebhookapiv1analyzev2webhookspost) | **POST** /api/v1/analyze/v2/webhooks | Register Webhook|
|[**scheduleAnalysisApiV1AnalyzeV2SchedulesPost**](#scheduleanalysisapiv1analyzev2schedulespost) | **POST** /api/v1/analyze/v2/schedules | Schedule Analysis|
|[**sendIntegrationNotificationApiV1AnalyzeV2IntegrationsIntegrationIdNotifyPost**](#sendintegrationnotificationapiv1analyzev2integrationsintegrationidnotifypost) | **POST** /api/v1/analyze/v2/integrations/{integration_id}/notify | Send Integration Notification|
|[**sendWebhookTestApiV1AnalyzeV2WebhooksWebhookIdSendPost**](#sendwebhooktestapiv1analyzev2webhookswebhookidsendpost) | **POST** /api/v1/analyze/v2/webhooks/{webhook_id}/send | Send Webhook Test|

# **addCommentApiV1AnalyzeV2AnalysisIdCommentsPost**
> any addCommentApiV1AnalyzeV2AnalysisIdCommentsPost(backendAppApiAnalyzeEnhancedAnalysisRoutesCommentRequest)

Add a comment to an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    BackendAppApiAnalyzeEnhancedAnalysisRoutesCommentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let backendAppApiAnalyzeEnhancedAnalysisRoutesCommentRequest: BackendAppApiAnalyzeEnhancedAnalysisRoutesCommentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addCommentApiV1AnalyzeV2AnalysisIdCommentsPost(
    analysisId,
    backendAppApiAnalyzeEnhancedAnalysisRoutesCommentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiAnalyzeEnhancedAnalysisRoutesCommentRequest** | **BackendAppApiAnalyzeEnhancedAnalysisRoutesCommentRequest**|  | |
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

# **analyzeDocumentApiV1AnalyzeV2UploadPost**
> any analyzeDocumentApiV1AnalyzeV2UploadPost()

Upload and analyze a document with AI-powered analysis.  Returns streaming NDJSON events with progress and final result.  **Features:** - Intelligent table extraction with cross-page stitching - Entity and metric extraction (dates, money, percentages, etc.) - Form and invoice parsing - Multi-mode summaries (executive, data, comprehensive, etc.) - Sentiment and tone analysis - Statistical analysis with outlier detection - Auto-generated visualizations - AI-powered insights, risks, and opportunities - Predictive analytics

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let file: File; // (default to undefined)
let background: boolean; //Run in background (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)
let preferences: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.analyzeDocumentApiV1AnalyzeV2UploadPost(
    file,
    background,
    xApiKey,
    preferences
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **background** | [**boolean**] | Run in background | (optional) defaults to false|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **preferences** | [**string**] |  | (optional) defaults to undefined|


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

# **askQuestionApiV1AnalyzeV2AnalysisIdAskPost**
> any askQuestionApiV1AnalyzeV2AnalysisIdAskPost(questionRequest)

Ask a natural language question about the analyzed document.  Uses RAG (Retrieval-Augmented Generation) to find relevant context and generate accurate answers with source citations.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    QuestionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let questionRequest: QuestionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.askQuestionApiV1AnalyzeV2AnalysisIdAskPost(
    analysisId,
    questionRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **questionRequest** | **QuestionRequest**|  | |
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

# **compareDocumentsApiV1AnalyzeV2ComparePost**
> any compareDocumentsApiV1AnalyzeV2ComparePost(backendAppApiAnalyzeEnhancedAnalysisRoutesCompareRequest)

Compare two analyzed documents.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    BackendAppApiAnalyzeEnhancedAnalysisRoutesCompareRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let backendAppApiAnalyzeEnhancedAnalysisRoutesCompareRequest: BackendAppApiAnalyzeEnhancedAnalysisRoutesCompareRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.compareDocumentsApiV1AnalyzeV2ComparePost(
    backendAppApiAnalyzeEnhancedAnalysisRoutesCompareRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiAnalyzeEnhancedAnalysisRoutesCompareRequest** | **BackendAppApiAnalyzeEnhancedAnalysisRoutesCompareRequest**|  | |
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

# **createIntegrationItemApiV1AnalyzeV2IntegrationsIntegrationIdItemsPost**
> any createIntegrationItemApiV1AnalyzeV2IntegrationsIntegrationIdItemsPost(integrationItemRequest)

Create an item (ticket/task) in an external integration.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    IntegrationItemRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let integrationId: string; // (default to undefined)
let integrationItemRequest: IntegrationItemRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createIntegrationItemApiV1AnalyzeV2IntegrationsIntegrationIdItemsPost(
    integrationId,
    integrationItemRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **integrationItemRequest** | **IntegrationItemRequest**|  | |
| **integrationId** | [**string**] |  | defaults to undefined|
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

# **createPipelineApiV1AnalyzeV2PipelinesPost**
> any createPipelineApiV1AnalyzeV2PipelinesPost(pipelineRequest)

Create a workflow pipeline.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    PipelineRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let pipelineRequest: PipelineRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPipelineApiV1AnalyzeV2PipelinesPost(
    pipelineRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pipelineRequest** | **PipelineRequest**|  | |
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

# **createShareLinkApiV1AnalyzeV2AnalysisIdSharePost**
> any createShareLinkApiV1AnalyzeV2AnalysisIdSharePost(shareRequest)

Create a shareable link for an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    ShareRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let shareRequest: ShareRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createShareLinkApiV1AnalyzeV2AnalysisIdSharePost(
    analysisId,
    shareRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **shareRequest** | **ShareRequest**|  | |
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

# **createTriggerApiV1AnalyzeV2TriggersPost**
> any createTriggerApiV1AnalyzeV2TriggersPost(triggerRequest)

Create a workflow trigger.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    TriggerRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let triggerRequest: TriggerRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTriggerApiV1AnalyzeV2TriggersPost(
    triggerRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **triggerRequest** | **TriggerRequest**|  | |
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

# **executePipelineApiV1AnalyzeV2PipelinesPipelineIdExecutePost**
> any executePipelineApiV1AnalyzeV2PipelinesPipelineIdExecutePost(pipelineExecuteRequest)

Execute a workflow pipeline.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    PipelineExecuteRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let pipelineId: string; // (default to undefined)
let pipelineExecuteRequest: PipelineExecuteRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.executePipelineApiV1AnalyzeV2PipelinesPipelineIdExecutePost(
    pipelineId,
    pipelineExecuteRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pipelineExecuteRequest** | **PipelineExecuteRequest**|  | |
| **pipelineId** | [**string**] |  | defaults to undefined|
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

# **exportAnalysisApiV1AnalyzeV2AnalysisIdExportPost**
> any exportAnalysisApiV1AnalyzeV2AnalysisIdExportPost(exportRequest)

Export analysis in various formats.  Supported formats: - json: Full analysis as JSON - csv: Tables as CSV - excel: Formatted Excel workbook - pdf: PDF report - markdown: Markdown document - html: HTML report

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    ExportRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let exportRequest: ExportRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportAnalysisApiV1AnalyzeV2AnalysisIdExportPost(
    analysisId,
    exportRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportRequest** | **ExportRequest**|  | |
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

# **fetchDataFromSourceApiV1AnalyzeV2SourcesConnectionIdFetchPost**
> any fetchDataFromSourceApiV1AnalyzeV2SourcesConnectionIdFetchPost(dataFetchRequest)

Fetch data from a registered data source.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    DataFetchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let connectionId: string; // (default to undefined)
let dataFetchRequest: DataFetchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.fetchDataFromSourceApiV1AnalyzeV2SourcesConnectionIdFetchPost(
    connectionId,
    dataFetchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dataFetchRequest** | **DataFetchRequest**|  | |
| **connectionId** | [**string**] |  | defaults to undefined|
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

# **generateChartsApiV1AnalyzeV2AnalysisIdChartsGeneratePost**
> any generateChartsApiV1AnalyzeV2AnalysisIdChartsGeneratePost(chartRequest)

Generate charts from natural language query.  Examples: - \"Show me revenue by quarter as a line chart\" - \"Compare sales across regions\" - \"Create a pie chart of market share\"

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    ChartRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let chartRequest: ChartRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateChartsApiV1AnalyzeV2AnalysisIdChartsGeneratePost(
    analysisId,
    chartRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chartRequest** | **ChartRequest**|  | |
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

# **getAnalysisApiV1AnalyzeV2AnalysisIdGet**
> any getAnalysisApiV1AnalyzeV2AnalysisIdGet()

Get a previously computed analysis result.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAnalysisApiV1AnalyzeV2AnalysisIdGet(
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

# **getChartTypesApiV1AnalyzeV2ConfigChartTypesGet**
> any getChartTypesApiV1AnalyzeV2ConfigChartTypesGet()

Get available chart types.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getChartTypesApiV1AnalyzeV2ConfigChartTypesGet(
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

# **getChartsApiV1AnalyzeV2AnalysisIdChartsGet**
> any getChartsApiV1AnalyzeV2AnalysisIdChartsGet()

Get all charts for an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getChartsApiV1AnalyzeV2AnalysisIdChartsGet(
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

# **getCommentsApiV1AnalyzeV2AnalysisIdCommentsGet**
> any getCommentsApiV1AnalyzeV2AnalysisIdCommentsGet()

Get all comments for an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCommentsApiV1AnalyzeV2AnalysisIdCommentsGet(
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

# **getDataQualityApiV1AnalyzeV2AnalysisIdQualityGet**
> any getDataQualityApiV1AnalyzeV2AnalysisIdQualityGet()

Get data quality assessment for an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDataQualityApiV1AnalyzeV2AnalysisIdQualityGet(
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

# **getEntitiesApiV1AnalyzeV2AnalysisIdEntitiesGet**
> any getEntitiesApiV1AnalyzeV2AnalysisIdEntitiesGet()

Get extracted entities from an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getEntitiesApiV1AnalyzeV2AnalysisIdEntitiesGet(
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

# **getExportFormatsApiV1AnalyzeV2ConfigExportFormatsGet**
> any getExportFormatsApiV1AnalyzeV2ConfigExportFormatsGet()

Get available export formats.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExportFormatsApiV1AnalyzeV2ConfigExportFormatsGet(
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

# **getIndustryOptionsApiV1AnalyzeV2ConfigIndustriesGet**
> any getIndustryOptionsApiV1AnalyzeV2ConfigIndustriesGet()

Get available industry options for analysis configuration.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getIndustryOptionsApiV1AnalyzeV2ConfigIndustriesGet(
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

# **getInsightsApiV1AnalyzeV2AnalysisIdInsightsGet**
> any getInsightsApiV1AnalyzeV2AnalysisIdInsightsGet()

Get AI-generated insights, risks, and opportunities.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getInsightsApiV1AnalyzeV2AnalysisIdInsightsGet(
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

# **getMetricsApiV1AnalyzeV2AnalysisIdMetricsGet**
> any getMetricsApiV1AnalyzeV2AnalysisIdMetricsGet()

Get extracted metrics from an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMetricsApiV1AnalyzeV2AnalysisIdMetricsGet(
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

# **getSharedAnalysisApiV1AnalyzeV2SharedShareIdGet**
> any getSharedAnalysisApiV1AnalyzeV2SharedShareIdGet()

Retrieve a shared analysis by share link.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let shareId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSharedAnalysisApiV1AnalyzeV2SharedShareIdGet(
    shareId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **shareId** | [**string**] |  | defaults to undefined|
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

# **getSuggestedQuestionsApiV1AnalyzeV2AnalysisIdSuggestedQuestionsGet**
> any getSuggestedQuestionsApiV1AnalyzeV2AnalysisIdSuggestedQuestionsGet()

Get AI-generated suggested questions for an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSuggestedQuestionsApiV1AnalyzeV2AnalysisIdSuggestedQuestionsGet(
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

# **getSummaryApiV1AnalyzeV2AnalysisIdSummaryModeGet**
> any getSummaryApiV1AnalyzeV2AnalysisIdSummaryModeGet()

Get a specific summary mode for an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let mode: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSummaryApiV1AnalyzeV2AnalysisIdSummaryModeGet(
    analysisId,
    mode,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **analysisId** | [**string**] |  | defaults to undefined|
| **mode** | [**string**] |  | defaults to undefined|
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

# **getSummaryModesApiV1AnalyzeV2ConfigSummaryModesGet**
> any getSummaryModesApiV1AnalyzeV2ConfigSummaryModesGet()

Get available summary modes.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSummaryModesApiV1AnalyzeV2ConfigSummaryModesGet(
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

# **getTablesApiV1AnalyzeV2AnalysisIdTablesGet**
> any getTablesApiV1AnalyzeV2AnalysisIdTablesGet()

Get extracted tables from an analysis.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let analysisId: string; // (default to undefined)
let limit: number; // (optional) (default to 10)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTablesApiV1AnalyzeV2AnalysisIdTablesGet(
    analysisId,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **analysisId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 10|
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

# **listDataSourcesApiV1AnalyzeV2SourcesGet**
> any listDataSourcesApiV1AnalyzeV2SourcesGet()

List registered data sources.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDataSourcesApiV1AnalyzeV2SourcesGet(
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

# **listIntegrationsApiV1AnalyzeV2IntegrationsGet**
> any listIntegrationsApiV1AnalyzeV2IntegrationsGet()

List registered external integrations.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listIntegrationsApiV1AnalyzeV2IntegrationsGet(
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

# **registerDataSourceApiV1AnalyzeV2SourcesPost**
> any registerDataSourceApiV1AnalyzeV2SourcesPost(dataSourceRequest)

Register a data source connection.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    DataSourceRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let dataSourceRequest: DataSourceRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.registerDataSourceApiV1AnalyzeV2SourcesPost(
    dataSourceRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dataSourceRequest** | **DataSourceRequest**|  | |
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

# **registerIntegrationApiV1AnalyzeV2IntegrationsPost**
> any registerIntegrationApiV1AnalyzeV2IntegrationsPost(integrationRequest)

Register an external integration (Slack/Teams/Jira/Email).

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    IntegrationRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let integrationRequest: IntegrationRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.registerIntegrationApiV1AnalyzeV2IntegrationsPost(
    integrationRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **integrationRequest** | **IntegrationRequest**|  | |
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

# **registerWebhookApiV1AnalyzeV2WebhooksPost**
> any registerWebhookApiV1AnalyzeV2WebhooksPost(webhookRequest)

Register a webhook for analysis events.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    WebhookRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let webhookRequest: WebhookRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.registerWebhookApiV1AnalyzeV2WebhooksPost(
    webhookRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookRequest** | **WebhookRequest**|  | |
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

# **scheduleAnalysisApiV1AnalyzeV2SchedulesPost**
> any scheduleAnalysisApiV1AnalyzeV2SchedulesPost(scheduleRequest)

Schedule a recurring analysis workflow.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    ScheduleRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let scheduleRequest: ScheduleRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scheduleAnalysisApiV1AnalyzeV2SchedulesPost(
    scheduleRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scheduleRequest** | **ScheduleRequest**|  | |
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

# **sendIntegrationNotificationApiV1AnalyzeV2IntegrationsIntegrationIdNotifyPost**
> any sendIntegrationNotificationApiV1AnalyzeV2IntegrationsIntegrationIdNotifyPost(integrationMessageRequest)

Send a notification through an integration.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    IntegrationMessageRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let integrationId: string; // (default to undefined)
let integrationMessageRequest: IntegrationMessageRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.sendIntegrationNotificationApiV1AnalyzeV2IntegrationsIntegrationIdNotifyPost(
    integrationId,
    integrationMessageRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **integrationMessageRequest** | **IntegrationMessageRequest**|  | |
| **integrationId** | [**string**] |  | defaults to undefined|
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

# **sendWebhookTestApiV1AnalyzeV2WebhooksWebhookIdSendPost**
> any sendWebhookTestApiV1AnalyzeV2WebhooksWebhookIdSendPost(webhookSendRequest)

Send a test webhook event.

### Example

```typescript
import {
    EnhancedAnalysisApi,
    Configuration,
    WebhookSendRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnhancedAnalysisApi(configuration);

let webhookId: string; // (default to undefined)
let webhookSendRequest: WebhookSendRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.sendWebhookTestApiV1AnalyzeV2WebhooksWebhookIdSendPost(
    webhookId,
    webhookSendRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookSendRequest** | **WebhookSendRequest**|  | |
| **webhookId** | [**string**] |  | defaults to undefined|
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

