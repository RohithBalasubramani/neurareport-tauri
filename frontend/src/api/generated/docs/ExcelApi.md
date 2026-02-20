# ExcelApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedPost**](#createsavedchartexcelrouteapiv1exceltemplateidchartssavedpost) | **POST** /api/v1/excel/{template_id}/charts/saved | Create Saved Chart Excel Route|
|[**deleteSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedChartIdDelete**](#deletesavedchartexcelrouteapiv1exceltemplateidchartssavedchartiddelete) | **DELETE** /api/v1/excel/{template_id}/charts/saved/{chart_id} | Delete Saved Chart Excel Route|
|[**discoverReportsExcelApiV1ExcelReportsDiscoverPost**](#discoverreportsexcelapiv1excelreportsdiscoverpost) | **POST** /api/v1/excel/reports/discover | Discover Reports Excel|
|[**enqueueReportJobExcelApiV1ExcelJobsRunReportPost**](#enqueuereportjobexcelapiv1exceljobsrunreportpost) | **POST** /api/v1/excel/jobs/run-report | Enqueue Report Job Excel|
|[**generatorAssetsExcelRouteApiV1ExcelTemplateIdGeneratorAssetsV1Post**](#generatorassetsexcelrouteapiv1exceltemplateidgeneratorassetsv1post) | **POST** /api/v1/excel/{template_id}/generator-assets/v1 | Generator Assets Excel Route|
|[**getArtifactHeadExcelApiV1ExcelTemplateIdArtifactsHeadGet**](#getartifactheadexcelapiv1exceltemplateidartifactsheadget) | **GET** /api/v1/excel/{template_id}/artifacts/head | Get Artifact Head Excel|
|[**getArtifactManifestExcelApiV1ExcelTemplateIdArtifactsManifestGet**](#getartifactmanifestexcelapiv1exceltemplateidartifactsmanifestget) | **GET** /api/v1/excel/{template_id}/artifacts/manifest | Get Artifact Manifest Excel|
|[**listSavedChartsExcelRouteApiV1ExcelTemplateIdChartsSavedGet**](#listsavedchartsexcelrouteapiv1exceltemplateidchartssavedget) | **GET** /api/v1/excel/{template_id}/charts/saved | List Saved Charts Excel Route|
|[**mappingApproveExcelApiV1ExcelTemplateIdMappingApprovePost**](#mappingapproveexcelapiv1exceltemplateidmappingapprovepost) | **POST** /api/v1/excel/{template_id}/mapping/approve | Mapping Approve Excel|
|[**mappingCorrectionsPreviewExcelApiV1ExcelTemplateIdMappingCorrectionsPreviewPost**](#mappingcorrectionspreviewexcelapiv1exceltemplateidmappingcorrectionspreviewpost) | **POST** /api/v1/excel/{template_id}/mapping/corrections-preview | Mapping Corrections Preview Excel|
|[**mappingKeyOptionsExcelApiV1ExcelTemplateIdKeysOptionsGet**](#mappingkeyoptionsexcelapiv1exceltemplateidkeysoptionsget) | **GET** /api/v1/excel/{template_id}/keys/options | Mapping Key Options Excel|
|[**mappingPreviewExcelApiV1ExcelTemplateIdMappingPreviewPost**](#mappingpreviewexcelapiv1exceltemplateidmappingpreviewpost) | **POST** /api/v1/excel/{template_id}/mapping/preview | Mapping Preview Excel|
|[**runReportExcelApiV1ExcelReportsRunPost**](#runreportexcelapiv1excelreportsrunpost) | **POST** /api/v1/excel/reports/run | Run Report Excel|
|[**suggestChartsExcelRouteApiV1ExcelTemplateIdChartsSuggestPost**](#suggestchartsexcelrouteapiv1exceltemplateidchartssuggestpost) | **POST** /api/v1/excel/{template_id}/charts/suggest | Suggest Charts Excel Route|
|[**updateSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedChartIdPut**](#updatesavedchartexcelrouteapiv1exceltemplateidchartssavedchartidput) | **PUT** /api/v1/excel/{template_id}/charts/saved/{chart_id} | Update Saved Chart Excel Route|
|[**verifyExcelRouteApiV1ExcelVerifyPost**](#verifyexcelrouteapiv1excelverifypost) | **POST** /api/v1/excel/verify | Verify Excel Route|

# **createSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedPost**
> any createSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedPost(savedChartCreatePayload)

Create a saved chart for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    SavedChartCreatePayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let savedChartCreatePayload: SavedChartCreatePayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedPost(
    templateId,
    savedChartCreatePayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **savedChartCreatePayload** | **SavedChartCreatePayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **deleteSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedChartIdDelete**
> any deleteSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedChartIdDelete()

Delete a saved chart for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let chartId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedChartIdDelete(
    templateId,
    chartId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **chartId** | [**string**] |  | defaults to undefined|
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

# **discoverReportsExcelApiV1ExcelReportsDiscoverPost**
> any discoverReportsExcelApiV1ExcelReportsDiscoverPost(discoverPayload)

Discover available batches for Excel report generation.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    DiscoverPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let discoverPayload: DiscoverPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.discoverReportsExcelApiV1ExcelReportsDiscoverPost(
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

# **enqueueReportJobExcelApiV1ExcelJobsRunReportPost**
> any enqueueReportJobExcelApiV1ExcelJobsRunReportPost(payload)

Queue an Excel report job for async generation.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    Payload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let payload: Payload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.enqueueReportJobExcelApiV1ExcelJobsRunReportPost(
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

# **generatorAssetsExcelRouteApiV1ExcelTemplateIdGeneratorAssetsV1Post**
> any generatorAssetsExcelRouteApiV1ExcelTemplateIdGeneratorAssetsV1Post(generatorAssetsPayload)

Generate assets for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    GeneratorAssetsPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let generatorAssetsPayload: GeneratorAssetsPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generatorAssetsExcelRouteApiV1ExcelTemplateIdGeneratorAssetsV1Post(
    templateId,
    generatorAssetsPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **generatorAssetsPayload** | **GeneratorAssetsPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **getArtifactHeadExcelApiV1ExcelTemplateIdArtifactsHeadGet**
> any getArtifactHeadExcelApiV1ExcelTemplateIdArtifactsHeadGet()

Get the head (preview) of a specific artifact.

### Example

```typescript
import {
    ExcelApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let name: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getArtifactHeadExcelApiV1ExcelTemplateIdArtifactsHeadGet(
    templateId,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **name** | [**string**] |  | defaults to undefined|
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

# **getArtifactManifestExcelApiV1ExcelTemplateIdArtifactsManifestGet**
> any getArtifactManifestExcelApiV1ExcelTemplateIdArtifactsManifestGet()

Get the artifact manifest for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getArtifactManifestExcelApiV1ExcelTemplateIdArtifactsManifestGet(
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **listSavedChartsExcelRouteApiV1ExcelTemplateIdChartsSavedGet**
> any listSavedChartsExcelRouteApiV1ExcelTemplateIdChartsSavedGet()

List saved charts for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSavedChartsExcelRouteApiV1ExcelTemplateIdChartsSavedGet(
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **mappingApproveExcelApiV1ExcelTemplateIdMappingApprovePost**
> any mappingApproveExcelApiV1ExcelTemplateIdMappingApprovePost(mappingPayload)

Approve mapping for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    MappingPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let mappingPayload: MappingPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mappingApproveExcelApiV1ExcelTemplateIdMappingApprovePost(
    templateId,
    mappingPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **mappingPayload** | **MappingPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **mappingCorrectionsPreviewExcelApiV1ExcelTemplateIdMappingCorrectionsPreviewPost**
> any mappingCorrectionsPreviewExcelApiV1ExcelTemplateIdMappingCorrectionsPreviewPost(correctionsPreviewPayload)

Preview corrections for Excel template mapping.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    CorrectionsPreviewPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let correctionsPreviewPayload: CorrectionsPreviewPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mappingCorrectionsPreviewExcelApiV1ExcelTemplateIdMappingCorrectionsPreviewPost(
    templateId,
    correctionsPreviewPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **correctionsPreviewPayload** | **CorrectionsPreviewPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **mappingKeyOptionsExcelApiV1ExcelTemplateIdKeysOptionsGet**
> any mappingKeyOptionsExcelApiV1ExcelTemplateIdKeysOptionsGet()

Get available key options for Excel template filtering.

### Example

```typescript
import {
    ExcelApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let connectionId: string; // (optional) (default to undefined)
let tokens: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 500)
let startDate: string; // (optional) (default to undefined)
let endDate: string; // (optional) (default to undefined)
let debug: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mappingKeyOptionsExcelApiV1ExcelTemplateIdKeysOptionsGet(
    templateId,
    connectionId,
    tokens,
    limit,
    startDate,
    endDate,
    debug,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|
| **tokens** | [**string**] |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 500|
| **startDate** | [**string**] |  | (optional) defaults to undefined|
| **endDate** | [**string**] |  | (optional) defaults to undefined|
| **debug** | [**boolean**] |  | (optional) defaults to false|
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

# **mappingPreviewExcelApiV1ExcelTemplateIdMappingPreviewPost**
> any mappingPreviewExcelApiV1ExcelTemplateIdMappingPreviewPost()

Preview mapping for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let connectionId: string; // (default to undefined)
let forceRefresh: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mappingPreviewExcelApiV1ExcelTemplateIdMappingPreviewPost(
    templateId,
    connectionId,
    forceRefresh,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **connectionId** | [**string**] |  | defaults to undefined|
| **forceRefresh** | [**boolean**] |  | (optional) defaults to false|
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

# **runReportExcelApiV1ExcelReportsRunPost**
> any runReportExcelApiV1ExcelReportsRunPost(runPayload)

Run an Excel report synchronously.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    RunPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let runPayload: RunPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runReportExcelApiV1ExcelReportsRunPost(
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

# **suggestChartsExcelRouteApiV1ExcelTemplateIdChartsSuggestPost**
> any suggestChartsExcelRouteApiV1ExcelTemplateIdChartsSuggestPost(chartSuggestPayload)

Get chart suggestions for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    ChartSuggestPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let chartSuggestPayload: ChartSuggestPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestChartsExcelRouteApiV1ExcelTemplateIdChartsSuggestPost(
    templateId,
    chartSuggestPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chartSuggestPayload** | **ChartSuggestPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **updateSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedChartIdPut**
> any updateSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedChartIdPut(savedChartUpdatePayload)

Update a saved chart for an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration,
    SavedChartUpdatePayload
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let templateId: string; // (default to undefined)
let chartId: string; // (default to undefined)
let savedChartUpdatePayload: SavedChartUpdatePayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSavedChartExcelRouteApiV1ExcelTemplateIdChartsSavedChartIdPut(
    templateId,
    chartId,
    savedChartUpdatePayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **savedChartUpdatePayload** | **SavedChartUpdatePayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
| **chartId** | [**string**] |  | defaults to undefined|
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

# **verifyExcelRouteApiV1ExcelVerifyPost**
> any verifyExcelRouteApiV1ExcelVerifyPost()

Verify and process an Excel template.

### Example

```typescript
import {
    ExcelApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExcelApi(configuration);

let file: File; // (default to undefined)
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)
let connectionId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.verifyExcelRouteApiV1ExcelVerifyPost(
    file,
    background,
    xApiKey,
    connectionId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **background** | [**boolean**] |  | (optional) defaults to false|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|


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

