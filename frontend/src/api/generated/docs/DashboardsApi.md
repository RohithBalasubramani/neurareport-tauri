# DashboardsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addDashboardFilterApiV1DashboardsDashboardIdFiltersPost**](#adddashboardfilterapiv1dashboardsdashboardidfilterspost) | **POST** /api/v1/dashboards/{dashboard_id}/filters | Add Dashboard Filter|
|[**addDashboardFilterApiV1DashboardsDashboardIdFiltersPost_0**](#adddashboardfilterapiv1dashboardsdashboardidfilterspost_0) | **POST** /api/v1/dashboards/{dashboard_id}/filters | Add Dashboard Filter|
|[**addWidgetApiV1DashboardsDashboardIdWidgetsPost**](#addwidgetapiv1dashboardsdashboardidwidgetspost) | **POST** /api/v1/dashboards/{dashboard_id}/widgets | Add Widget|
|[**addWidgetApiV1DashboardsDashboardIdWidgetsPost_0**](#addwidgetapiv1dashboardsdashboardidwidgetspost_0) | **POST** /api/v1/dashboards/{dashboard_id}/widgets | Add Widget|
|[**createDashboardApiV1DashboardsPost**](#createdashboardapiv1dashboardspost) | **POST** /api/v1/dashboards | Create Dashboard|
|[**createDashboardApiV1DashboardsPost_0**](#createdashboardapiv1dashboardspost_0) | **POST** /api/v1/dashboards | Create Dashboard|
|[**createDashboardFromTemplateApiV1DashboardsTemplatesTemplateIdCreatePost**](#createdashboardfromtemplateapiv1dashboardstemplatestemplateidcreatepost) | **POST** /api/v1/dashboards/templates/{template_id}/create | Create Dashboard From Template|
|[**createDashboardFromTemplateApiV1DashboardsTemplatesTemplateIdCreatePost_0**](#createdashboardfromtemplateapiv1dashboardstemplatestemplateidcreatepost_0) | **POST** /api/v1/dashboards/templates/{template_id}/create | Create Dashboard From Template|
|[**createSnapshotApiV1DashboardsDashboardIdSnapshotPost**](#createsnapshotapiv1dashboardsdashboardidsnapshotpost) | **POST** /api/v1/dashboards/{dashboard_id}/snapshot | Create Snapshot|
|[**createSnapshotApiV1DashboardsDashboardIdSnapshotPost_0**](#createsnapshotapiv1dashboardsdashboardidsnapshotpost_0) | **POST** /api/v1/dashboards/{dashboard_id}/snapshot | Create Snapshot|
|[**deleteDashboardApiV1DashboardsDashboardIdDelete**](#deletedashboardapiv1dashboardsdashboardiddelete) | **DELETE** /api/v1/dashboards/{dashboard_id} | Delete Dashboard|
|[**deleteDashboardApiV1DashboardsDashboardIdDelete_0**](#deletedashboardapiv1dashboardsdashboardiddelete_0) | **DELETE** /api/v1/dashboards/{dashboard_id} | Delete Dashboard|
|[**deleteDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdDelete**](#deletedashboardfilterapiv1dashboardsdashboardidfiltersfilteriddelete) | **DELETE** /api/v1/dashboards/{dashboard_id}/filters/{filter_id} | Delete Dashboard Filter|
|[**deleteDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdDelete_0**](#deletedashboardfilterapiv1dashboardsdashboardidfiltersfilteriddelete_0) | **DELETE** /api/v1/dashboards/{dashboard_id}/filters/{filter_id} | Delete Dashboard Filter|
|[**deleteWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdDelete**](#deletewidgetapiv1dashboardsdashboardidwidgetswidgetiddelete) | **DELETE** /api/v1/dashboards/{dashboard_id}/widgets/{widget_id} | Delete Widget|
|[**deleteWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdDelete_0**](#deletewidgetapiv1dashboardsdashboardidwidgetswidgetiddelete_0) | **DELETE** /api/v1/dashboards/{dashboard_id}/widgets/{widget_id} | Delete Widget|
|[**detectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost**](#detectanomaliesapiv1dashboardsanalyticsanomaliespost) | **POST** /api/v1/dashboards/analytics/anomalies | Detect Anomalies|
|[**detectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost_0**](#detectanomaliesapiv1dashboardsanalyticsanomaliespost_0) | **POST** /api/v1/dashboards/analytics/anomalies | Detect Anomalies|
|[**executeWidgetQueryApiV1DashboardsDashboardIdQueryPost**](#executewidgetqueryapiv1dashboardsdashboardidquerypost) | **POST** /api/v1/dashboards/{dashboard_id}/query | Execute Widget Query|
|[**executeWidgetQueryApiV1DashboardsDashboardIdQueryPost_0**](#executewidgetqueryapiv1dashboardsdashboardidquerypost_0) | **POST** /api/v1/dashboards/{dashboard_id}/query | Execute Widget Query|
|[**exportDashboardApiV1DashboardsDashboardIdExportGet**](#exportdashboardapiv1dashboardsdashboardidexportget) | **GET** /api/v1/dashboards/{dashboard_id}/export | Export Dashboard|
|[**exportDashboardApiV1DashboardsDashboardIdExportGet_0**](#exportdashboardapiv1dashboardsdashboardidexportget_0) | **GET** /api/v1/dashboards/{dashboard_id}/export | Export Dashboard|
|[**findCorrelationsApiV1DashboardsAnalyticsCorrelationsPost**](#findcorrelationsapiv1dashboardsanalyticscorrelationspost) | **POST** /api/v1/dashboards/analytics/correlations | Find Correlations|
|[**findCorrelationsApiV1DashboardsAnalyticsCorrelationsPost_0**](#findcorrelationsapiv1dashboardsanalyticscorrelationspost_0) | **POST** /api/v1/dashboards/analytics/correlations | Find Correlations|
|[**generateEmbedTokenApiV1DashboardsDashboardIdEmbedPost**](#generateembedtokenapiv1dashboardsdashboardidembedpost) | **POST** /api/v1/dashboards/{dashboard_id}/embed | Generate Embed Token|
|[**generateEmbedTokenApiV1DashboardsDashboardIdEmbedPost_0**](#generateembedtokenapiv1dashboardsdashboardidembedpost_0) | **POST** /api/v1/dashboards/{dashboard_id}/embed | Generate Embed Token|
|[**generateInsightsApiV1DashboardsAnalyticsInsightsPost**](#generateinsightsapiv1dashboardsanalyticsinsightspost) | **POST** /api/v1/dashboards/analytics/insights | Generate Insights|
|[**generateInsightsApiV1DashboardsAnalyticsInsightsPost_0**](#generateinsightsapiv1dashboardsanalyticsinsightspost_0) | **POST** /api/v1/dashboards/analytics/insights | Generate Insights|
|[**getDashboardApiV1DashboardsDashboardIdGet**](#getdashboardapiv1dashboardsdashboardidget) | **GET** /api/v1/dashboards/{dashboard_id} | Get Dashboard|
|[**getDashboardApiV1DashboardsDashboardIdGet_0**](#getdashboardapiv1dashboardsdashboardidget_0) | **GET** /api/v1/dashboards/{dashboard_id} | Get Dashboard|
|[**getSnapshotApiV1DashboardsSnapshotsSnapshotIdGet**](#getsnapshotapiv1dashboardssnapshotssnapshotidget) | **GET** /api/v1/dashboards/snapshots/{snapshot_id} | Get Snapshot|
|[**getSnapshotApiV1DashboardsSnapshotsSnapshotIdGet_0**](#getsnapshotapiv1dashboardssnapshotssnapshotidget_0) | **GET** /api/v1/dashboards/snapshots/{snapshot_id} | Get Snapshot|
|[**listDashboardTemplatesApiV1DashboardsTemplatesGet**](#listdashboardtemplatesapiv1dashboardstemplatesget) | **GET** /api/v1/dashboards/templates | List Dashboard Templates|
|[**listDashboardTemplatesApiV1DashboardsTemplatesGet_0**](#listdashboardtemplatesapiv1dashboardstemplatesget_0) | **GET** /api/v1/dashboards/templates | List Dashboard Templates|
|[**listDashboardsApiV1DashboardsGet**](#listdashboardsapiv1dashboardsget) | **GET** /api/v1/dashboards | List Dashboards|
|[**listDashboardsApiV1DashboardsGet_0**](#listdashboardsapiv1dashboardsget_0) | **GET** /api/v1/dashboards | List Dashboards|
|[**predictTrendsApiV1DashboardsAnalyticsTrendsPost**](#predicttrendsapiv1dashboardsanalyticstrendspost) | **POST** /api/v1/dashboards/analytics/trends | Predict Trends|
|[**predictTrendsApiV1DashboardsAnalyticsTrendsPost_0**](#predicttrendsapiv1dashboardsanalyticstrendspost_0) | **POST** /api/v1/dashboards/analytics/trends | Predict Trends|
|[**refreshDashboardApiV1DashboardsDashboardIdRefreshPost**](#refreshdashboardapiv1dashboardsdashboardidrefreshpost) | **POST** /api/v1/dashboards/{dashboard_id}/refresh | Refresh Dashboard|
|[**refreshDashboardApiV1DashboardsDashboardIdRefreshPost_0**](#refreshdashboardapiv1dashboardsdashboardidrefreshpost_0) | **POST** /api/v1/dashboards/{dashboard_id}/refresh | Refresh Dashboard|
|[**runWhatIfSimulationApiV1DashboardsDashboardIdWhatIfPost**](#runwhatifsimulationapiv1dashboardsdashboardidwhatifpost) | **POST** /api/v1/dashboards/{dashboard_id}/what-if | Run What If Simulation|
|[**runWhatIfSimulationApiV1DashboardsDashboardIdWhatIfPost_0**](#runwhatifsimulationapiv1dashboardsdashboardidwhatifpost_0) | **POST** /api/v1/dashboards/{dashboard_id}/what-if | Run What If Simulation|
|[**saveDashboardAsTemplateApiV1DashboardsDashboardIdSaveAsTemplatePost**](#savedashboardastemplateapiv1dashboardsdashboardidsaveastemplatepost) | **POST** /api/v1/dashboards/{dashboard_id}/save-as-template | Save Dashboard As Template|
|[**saveDashboardAsTemplateApiV1DashboardsDashboardIdSaveAsTemplatePost_0**](#savedashboardastemplateapiv1dashboardsdashboardidsaveastemplatepost_0) | **POST** /api/v1/dashboards/{dashboard_id}/save-as-template | Save Dashboard As Template|
|[**setDashboardVariableApiV1DashboardsDashboardIdVariablesVariableNamePut**](#setdashboardvariableapiv1dashboardsdashboardidvariablesvariablenameput) | **PUT** /api/v1/dashboards/{dashboard_id}/variables/{variable_name} | Set Dashboard Variable|
|[**setDashboardVariableApiV1DashboardsDashboardIdVariablesVariableNamePut_0**](#setdashboardvariableapiv1dashboardsdashboardidvariablesvariablenameput_0) | **PUT** /api/v1/dashboards/{dashboard_id}/variables/{variable_name} | Set Dashboard Variable|
|[**shareDashboardApiV1DashboardsDashboardIdSharePost**](#sharedashboardapiv1dashboardsdashboardidsharepost) | **POST** /api/v1/dashboards/{dashboard_id}/share | Share Dashboard|
|[**shareDashboardApiV1DashboardsDashboardIdSharePost_0**](#sharedashboardapiv1dashboardsdashboardidsharepost_0) | **POST** /api/v1/dashboards/{dashboard_id}/share | Share Dashboard|
|[**updateDashboardApiV1DashboardsDashboardIdPut**](#updatedashboardapiv1dashboardsdashboardidput) | **PUT** /api/v1/dashboards/{dashboard_id} | Update Dashboard|
|[**updateDashboardApiV1DashboardsDashboardIdPut_0**](#updatedashboardapiv1dashboardsdashboardidput_0) | **PUT** /api/v1/dashboards/{dashboard_id} | Update Dashboard|
|[**updateDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdPut**](#updatedashboardfilterapiv1dashboardsdashboardidfiltersfilteridput) | **PUT** /api/v1/dashboards/{dashboard_id}/filters/{filter_id} | Update Dashboard Filter|
|[**updateDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdPut_0**](#updatedashboardfilterapiv1dashboardsdashboardidfiltersfilteridput_0) | **PUT** /api/v1/dashboards/{dashboard_id}/filters/{filter_id} | Update Dashboard Filter|
|[**updateWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdPut**](#updatewidgetapiv1dashboardsdashboardidwidgetswidgetidput) | **PUT** /api/v1/dashboards/{dashboard_id}/widgets/{widget_id} | Update Widget|
|[**updateWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdPut_0**](#updatewidgetapiv1dashboardsdashboardidwidgetswidgetidput_0) | **PUT** /api/v1/dashboards/{dashboard_id}/widgets/{widget_id} | Update Widget|
|[**updateWidgetLayoutApiV1DashboardsDashboardIdLayoutPut**](#updatewidgetlayoutapiv1dashboardsdashboardidlayoutput) | **PUT** /api/v1/dashboards/{dashboard_id}/layout | Update Widget Layout|
|[**updateWidgetLayoutApiV1DashboardsDashboardIdLayoutPut_0**](#updatewidgetlayoutapiv1dashboardsdashboardidlayoutput_0) | **PUT** /api/v1/dashboards/{dashboard_id}/layout | Update Widget Layout|

# **addDashboardFilterApiV1DashboardsDashboardIdFiltersPost**
> any addDashboardFilterApiV1DashboardsDashboardIdFiltersPost(dashboardFilterRequest)

Add a filter to a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    DashboardFilterRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let dashboardFilterRequest: DashboardFilterRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDashboardFilterApiV1DashboardsDashboardIdFiltersPost(
    dashboardId,
    dashboardFilterRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardFilterRequest** | **DashboardFilterRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **addDashboardFilterApiV1DashboardsDashboardIdFiltersPost_0**
> any addDashboardFilterApiV1DashboardsDashboardIdFiltersPost_0(dashboardFilterRequest)

Add a filter to a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    DashboardFilterRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let dashboardFilterRequest: DashboardFilterRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDashboardFilterApiV1DashboardsDashboardIdFiltersPost_0(
    dashboardId,
    dashboardFilterRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardFilterRequest** | **DashboardFilterRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **addWidgetApiV1DashboardsDashboardIdWidgetsPost**
> any addWidgetApiV1DashboardsDashboardIdWidgetsPost(addWidgetRequest)

Add a widget to a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    AddWidgetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let addWidgetRequest: AddWidgetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addWidgetApiV1DashboardsDashboardIdWidgetsPost(
    dashboardId,
    addWidgetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **addWidgetRequest** | **AddWidgetRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **addWidgetApiV1DashboardsDashboardIdWidgetsPost_0**
> any addWidgetApiV1DashboardsDashboardIdWidgetsPost_0(addWidgetRequest)

Add a widget to a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    AddWidgetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let addWidgetRequest: AddWidgetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addWidgetApiV1DashboardsDashboardIdWidgetsPost_0(
    dashboardId,
    addWidgetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **addWidgetRequest** | **AddWidgetRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **createDashboardApiV1DashboardsPost**
> DashboardResponse createDashboardApiV1DashboardsPost(createDashboardRequest)

Create a new dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    CreateDashboardRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let createDashboardRequest: CreateDashboardRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createDashboardApiV1DashboardsPost(
    createDashboardRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createDashboardRequest** | **CreateDashboardRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardResponse**

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

# **createDashboardApiV1DashboardsPost_0**
> DashboardResponse createDashboardApiV1DashboardsPost_0(createDashboardRequest)

Create a new dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    CreateDashboardRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let createDashboardRequest: CreateDashboardRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createDashboardApiV1DashboardsPost_0(
    createDashboardRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createDashboardRequest** | **CreateDashboardRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardResponse**

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

# **createDashboardFromTemplateApiV1DashboardsTemplatesTemplateIdCreatePost**
> DashboardResponse createDashboardFromTemplateApiV1DashboardsTemplatesTemplateIdCreatePost()

Create a new dashboard from an existing template.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let templateId: string; // (default to undefined)
let name: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createDashboardFromTemplateApiV1DashboardsTemplatesTemplateIdCreatePost(
    templateId,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **name** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardResponse**

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

# **createDashboardFromTemplateApiV1DashboardsTemplatesTemplateIdCreatePost_0**
> DashboardResponse createDashboardFromTemplateApiV1DashboardsTemplatesTemplateIdCreatePost_0()

Create a new dashboard from an existing template.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let templateId: string; // (default to undefined)
let name: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createDashboardFromTemplateApiV1DashboardsTemplatesTemplateIdCreatePost_0(
    templateId,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **name** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardResponse**

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

# **createSnapshotApiV1DashboardsDashboardIdSnapshotPost**
> any createSnapshotApiV1DashboardsDashboardIdSnapshotPost()

Create a snapshot of the dashboard and trigger rendering.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let format: string; // (optional) (default to 'png')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSnapshotApiV1DashboardsDashboardIdSnapshotPost(
    dashboardId,
    format,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **format** | [**string**] |  | (optional) defaults to 'png'|
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

# **createSnapshotApiV1DashboardsDashboardIdSnapshotPost_0**
> any createSnapshotApiV1DashboardsDashboardIdSnapshotPost_0()

Create a snapshot of the dashboard and trigger rendering.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let format: string; // (optional) (default to 'png')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSnapshotApiV1DashboardsDashboardIdSnapshotPost_0(
    dashboardId,
    format,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **format** | [**string**] |  | (optional) defaults to 'png'|
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

# **deleteDashboardApiV1DashboardsDashboardIdDelete**
> any deleteDashboardApiV1DashboardsDashboardIdDelete()

Delete a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteDashboardApiV1DashboardsDashboardIdDelete(
    dashboardId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **deleteDashboardApiV1DashboardsDashboardIdDelete_0**
> any deleteDashboardApiV1DashboardsDashboardIdDelete_0()

Delete a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteDashboardApiV1DashboardsDashboardIdDelete_0(
    dashboardId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **deleteDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdDelete**
> any deleteDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdDelete()

Delete a filter from a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let filterId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdDelete(
    dashboardId,
    filterId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **filterId** | [**string**] |  | defaults to undefined|
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

# **deleteDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdDelete_0**
> any deleteDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdDelete_0()

Delete a filter from a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let filterId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdDelete_0(
    dashboardId,
    filterId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **filterId** | [**string**] |  | defaults to undefined|
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

# **deleteWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdDelete**
> any deleteWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdDelete()

Delete a widget from a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let widgetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdDelete(
    dashboardId,
    widgetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **widgetId** | [**string**] |  | defaults to undefined|
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

# **deleteWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdDelete_0**
> any deleteWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdDelete_0()

Delete a widget from a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let widgetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdDelete_0(
    dashboardId,
    widgetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **widgetId** | [**string**] |  | defaults to undefined|
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

# **detectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost**
> any detectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost(bodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost)

Detect anomalies in data.  Runs anomaly detection on each requested column via the analytics AnomalyService.  Results are aggregated across columns.  Note: only ``zscore`` method is currently implemented in the analytics engine.  ``iqr`` and ``isolation_forest`` are accepted for forward compatibility but fall back to z-score with a warning.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    BodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let bodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost: BodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost; //
let method: string; // (optional) (default to 'zscore')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.detectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost(
    bodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost,
    method,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost** | **BodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost**|  | |
| **method** | [**string**] |  | (optional) defaults to 'zscore'|
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

# **detectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost_0**
> any detectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost_0(bodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost)

Detect anomalies in data.  Runs anomaly detection on each requested column via the analytics AnomalyService.  Results are aggregated across columns.  Note: only ``zscore`` method is currently implemented in the analytics engine.  ``iqr`` and ``isolation_forest`` are accepted for forward compatibility but fall back to z-score with a warning.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    BodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let bodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost: BodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost; //
let method: string; // (optional) (default to 'zscore')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.detectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost_0(
    bodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost,
    method,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost** | **BodyDetectAnomaliesApiV1DashboardsAnalyticsAnomaliesPost**|  | |
| **method** | [**string**] |  | (optional) defaults to 'zscore'|
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

# **executeWidgetQueryApiV1DashboardsDashboardIdQueryPost**
> any executeWidgetQueryApiV1DashboardsDashboardIdQueryPost()

Execute a widget\'s query with optional filters.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let widgetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let requestBody: { [key: string]: any; }; // (optional)

const { status, data } = await apiInstance.executeWidgetQueryApiV1DashboardsDashboardIdQueryPost(
    dashboardId,
    widgetId,
    xApiKey,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **widgetId** | [**string**] |  | defaults to undefined|
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

# **executeWidgetQueryApiV1DashboardsDashboardIdQueryPost_0**
> any executeWidgetQueryApiV1DashboardsDashboardIdQueryPost_0()

Execute a widget\'s query with optional filters.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let widgetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let requestBody: { [key: string]: any; }; // (optional)

const { status, data } = await apiInstance.executeWidgetQueryApiV1DashboardsDashboardIdQueryPost_0(
    dashboardId,
    widgetId,
    xApiKey,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **widgetId** | [**string**] |  | defaults to undefined|
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

# **exportDashboardApiV1DashboardsDashboardIdExportGet**
> any exportDashboardApiV1DashboardsDashboardIdExportGet()

Export a complete dashboard and all its data as JSON.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportDashboardApiV1DashboardsDashboardIdExportGet(
    dashboardId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **exportDashboardApiV1DashboardsDashboardIdExportGet_0**
> any exportDashboardApiV1DashboardsDashboardIdExportGet_0()

Export a complete dashboard and all its data as JSON.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportDashboardApiV1DashboardsDashboardIdExportGet_0(
    dashboardId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **findCorrelationsApiV1DashboardsAnalyticsCorrelationsPost**
> any findCorrelationsApiV1DashboardsAnalyticsCorrelationsPost(bodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost)

Find correlations between columns.  Extracts numeric columns from the data dicts and delegates to the analytics CorrelationService.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    BodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let bodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost: BodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.findCorrelationsApiV1DashboardsAnalyticsCorrelationsPost(
    bodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost** | **BodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost**|  | |
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

# **findCorrelationsApiV1DashboardsAnalyticsCorrelationsPost_0**
> any findCorrelationsApiV1DashboardsAnalyticsCorrelationsPost_0(bodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost)

Find correlations between columns.  Extracts numeric columns from the data dicts and delegates to the analytics CorrelationService.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    BodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let bodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost: BodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.findCorrelationsApiV1DashboardsAnalyticsCorrelationsPost_0(
    bodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost** | **BodyFindCorrelationsApiV1DashboardsAnalyticsCorrelationsPost**|  | |
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

# **generateEmbedTokenApiV1DashboardsDashboardIdEmbedPost**
> any generateEmbedTokenApiV1DashboardsDashboardIdEmbedPost()

Generate an embed token for the dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let expiresHours: number; // (optional) (default to 24)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateEmbedTokenApiV1DashboardsDashboardIdEmbedPost(
    dashboardId,
    expiresHours,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **expiresHours** | [**number**] |  | (optional) defaults to 24|
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

# **generateEmbedTokenApiV1DashboardsDashboardIdEmbedPost_0**
> any generateEmbedTokenApiV1DashboardsDashboardIdEmbedPost_0()

Generate an embed token for the dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let expiresHours: number; // (optional) (default to 24)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateEmbedTokenApiV1DashboardsDashboardIdEmbedPost_0(
    dashboardId,
    expiresHours,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **expiresHours** | [**number**] |  | (optional) defaults to 24|
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

# **generateInsightsApiV1DashboardsAnalyticsInsightsPost**
> any generateInsightsApiV1DashboardsAnalyticsInsightsPost(requestBody)

Generate AI insights from data.  Converts raw data dicts into DataSeries and delegates to the analytics InsightService.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let requestBody: Array<{ [key: string]: any; }>; //
let context: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateInsightsApiV1DashboardsAnalyticsInsightsPost(
    requestBody,
    context,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<{ [key: string]: any; }>**|  | |
| **context** | [**string**] |  | (optional) defaults to undefined|
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

# **generateInsightsApiV1DashboardsAnalyticsInsightsPost_0**
> any generateInsightsApiV1DashboardsAnalyticsInsightsPost_0(requestBody)

Generate AI insights from data.  Converts raw data dicts into DataSeries and delegates to the analytics InsightService.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let requestBody: Array<{ [key: string]: any; }>; //
let context: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateInsightsApiV1DashboardsAnalyticsInsightsPost_0(
    requestBody,
    context,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<{ [key: string]: any; }>**|  | |
| **context** | [**string**] |  | (optional) defaults to undefined|
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

# **getDashboardApiV1DashboardsDashboardIdGet**
> DashboardResponse getDashboardApiV1DashboardsDashboardIdGet()

Get a dashboard by ID.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDashboardApiV1DashboardsDashboardIdGet(
    dashboardId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardResponse**

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

# **getDashboardApiV1DashboardsDashboardIdGet_0**
> DashboardResponse getDashboardApiV1DashboardsDashboardIdGet_0()

Get a dashboard by ID.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDashboardApiV1DashboardsDashboardIdGet_0(
    dashboardId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardResponse**

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

# **getSnapshotApiV1DashboardsSnapshotsSnapshotIdGet**
> any getSnapshotApiV1DashboardsSnapshotsSnapshotIdGet()

Get a snapshot by ID and return its URL and content hash.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let snapshotId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSnapshotApiV1DashboardsSnapshotsSnapshotIdGet(
    snapshotId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **snapshotId** | [**string**] |  | defaults to undefined|
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

# **getSnapshotApiV1DashboardsSnapshotsSnapshotIdGet_0**
> any getSnapshotApiV1DashboardsSnapshotsSnapshotIdGet_0()

Get a snapshot by ID and return its URL and content hash.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let snapshotId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSnapshotApiV1DashboardsSnapshotsSnapshotIdGet_0(
    snapshotId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **snapshotId** | [**string**] |  | defaults to undefined|
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

# **listDashboardTemplatesApiV1DashboardsTemplatesGet**
> any listDashboardTemplatesApiV1DashboardsTemplatesGet()

List available dashboard templates.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDashboardTemplatesApiV1DashboardsTemplatesGet(
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

# **listDashboardTemplatesApiV1DashboardsTemplatesGet_0**
> any listDashboardTemplatesApiV1DashboardsTemplatesGet_0()

List available dashboard templates.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDashboardTemplatesApiV1DashboardsTemplatesGet_0(
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

# **listDashboardsApiV1DashboardsGet**
> any listDashboardsApiV1DashboardsGet()

List all dashboards.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDashboardsApiV1DashboardsGet(
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 100|
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

# **listDashboardsApiV1DashboardsGet_0**
> any listDashboardsApiV1DashboardsGet_0()

List all dashboards.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDashboardsApiV1DashboardsGet_0(
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 100|
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

# **predictTrendsApiV1DashboardsAnalyticsTrendsPost**
> any predictTrendsApiV1DashboardsAnalyticsTrendsPost(requestBody)

Predict future trends from time series data.  Extracts the named value column from the data dicts and delegates to the analytics TrendService.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dateColumn: string; // (default to undefined)
let valueColumn: string; // (default to undefined)
let requestBody: Array<{ [key: string]: any; }>; //
let periods: number; // (optional) (default to 12)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.predictTrendsApiV1DashboardsAnalyticsTrendsPost(
    dateColumn,
    valueColumn,
    requestBody,
    periods,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<{ [key: string]: any; }>**|  | |
| **dateColumn** | [**string**] |  | defaults to undefined|
| **valueColumn** | [**string**] |  | defaults to undefined|
| **periods** | [**number**] |  | (optional) defaults to 12|
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

# **predictTrendsApiV1DashboardsAnalyticsTrendsPost_0**
> any predictTrendsApiV1DashboardsAnalyticsTrendsPost_0(requestBody)

Predict future trends from time series data.  Extracts the named value column from the data dicts and delegates to the analytics TrendService.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dateColumn: string; // (default to undefined)
let valueColumn: string; // (default to undefined)
let requestBody: Array<{ [key: string]: any; }>; //
let periods: number; // (optional) (default to 12)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.predictTrendsApiV1DashboardsAnalyticsTrendsPost_0(
    dateColumn,
    valueColumn,
    requestBody,
    periods,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<{ [key: string]: any; }>**|  | |
| **dateColumn** | [**string**] |  | defaults to undefined|
| **valueColumn** | [**string**] |  | defaults to undefined|
| **periods** | [**number**] |  | (optional) defaults to 12|
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

# **refreshDashboardApiV1DashboardsDashboardIdRefreshPost**
> any refreshDashboardApiV1DashboardsDashboardIdRefreshPost()

Refresh all widgets in a dashboard.  Retrieves the dashboard, iterates over its widgets, and returns a per-widget refresh status.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshDashboardApiV1DashboardsDashboardIdRefreshPost(
    dashboardId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **refreshDashboardApiV1DashboardsDashboardIdRefreshPost_0**
> any refreshDashboardApiV1DashboardsDashboardIdRefreshPost_0()

Refresh all widgets in a dashboard.  Retrieves the dashboard, iterates over its widgets, and returns a per-widget refresh status.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshDashboardApiV1DashboardsDashboardIdRefreshPost_0(
    dashboardId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **runWhatIfSimulationApiV1DashboardsDashboardIdWhatIfPost**
> any runWhatIfSimulationApiV1DashboardsDashboardIdWhatIfPost(backendAppApiRoutesDashboardsWhatIfRequest)

Run a what-if simulation on dashboard data.  Applies hypothetical variable changes and evaluates the requested metrics using the analytics services.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    BackendAppApiRoutesDashboardsWhatIfRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let backendAppApiRoutesDashboardsWhatIfRequest: BackendAppApiRoutesDashboardsWhatIfRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runWhatIfSimulationApiV1DashboardsDashboardIdWhatIfPost(
    dashboardId,
    backendAppApiRoutesDashboardsWhatIfRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesDashboardsWhatIfRequest** | **BackendAppApiRoutesDashboardsWhatIfRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **runWhatIfSimulationApiV1DashboardsDashboardIdWhatIfPost_0**
> any runWhatIfSimulationApiV1DashboardsDashboardIdWhatIfPost_0(backendAppApiRoutesDashboardsWhatIfRequest)

Run a what-if simulation on dashboard data.  Applies hypothetical variable changes and evaluates the requested metrics using the analytics services.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    BackendAppApiRoutesDashboardsWhatIfRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let backendAppApiRoutesDashboardsWhatIfRequest: BackendAppApiRoutesDashboardsWhatIfRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runWhatIfSimulationApiV1DashboardsDashboardIdWhatIfPost_0(
    dashboardId,
    backendAppApiRoutesDashboardsWhatIfRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesDashboardsWhatIfRequest** | **BackendAppApiRoutesDashboardsWhatIfRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **saveDashboardAsTemplateApiV1DashboardsDashboardIdSaveAsTemplatePost**
> any saveDashboardAsTemplateApiV1DashboardsDashboardIdSaveAsTemplatePost()

Save an existing dashboard as a reusable template.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let name: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.saveDashboardAsTemplateApiV1DashboardsDashboardIdSaveAsTemplatePost(
    dashboardId,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **name** | [**string**] |  | (optional) defaults to undefined|
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

# **saveDashboardAsTemplateApiV1DashboardsDashboardIdSaveAsTemplatePost_0**
> any saveDashboardAsTemplateApiV1DashboardsDashboardIdSaveAsTemplatePost_0()

Save an existing dashboard as a reusable template.

### Example

```typescript
import {
    DashboardsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let name: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.saveDashboardAsTemplateApiV1DashboardsDashboardIdSaveAsTemplatePost_0(
    dashboardId,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardId** | [**string**] |  | defaults to undefined|
| **name** | [**string**] |  | (optional) defaults to undefined|
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

# **setDashboardVariableApiV1DashboardsDashboardIdVariablesVariableNamePut**
> any setDashboardVariableApiV1DashboardsDashboardIdVariablesVariableNamePut(dashboardVariableRequest)

Set a dashboard variable value.  Stores the variable in the dashboard\'s metadata dict so it can be referenced by widget queries and filters.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    DashboardVariableRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let variableName: string; // (default to undefined)
let dashboardVariableRequest: DashboardVariableRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.setDashboardVariableApiV1DashboardsDashboardIdVariablesVariableNamePut(
    dashboardId,
    variableName,
    dashboardVariableRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardVariableRequest** | **DashboardVariableRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **variableName** | [**string**] |  | defaults to undefined|
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

# **setDashboardVariableApiV1DashboardsDashboardIdVariablesVariableNamePut_0**
> any setDashboardVariableApiV1DashboardsDashboardIdVariablesVariableNamePut_0(dashboardVariableRequest)

Set a dashboard variable value.  Stores the variable in the dashboard\'s metadata dict so it can be referenced by widget queries and filters.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    DashboardVariableRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let variableName: string; // (default to undefined)
let dashboardVariableRequest: DashboardVariableRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.setDashboardVariableApiV1DashboardsDashboardIdVariablesVariableNamePut_0(
    dashboardId,
    variableName,
    dashboardVariableRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardVariableRequest** | **DashboardVariableRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **variableName** | [**string**] |  | defaults to undefined|
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

# **shareDashboardApiV1DashboardsDashboardIdSharePost**
> any shareDashboardApiV1DashboardsDashboardIdSharePost(shareDashboardRequest)

Share a dashboard with other users.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    ShareDashboardRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let shareDashboardRequest: ShareDashboardRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.shareDashboardApiV1DashboardsDashboardIdSharePost(
    dashboardId,
    shareDashboardRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **shareDashboardRequest** | **ShareDashboardRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **shareDashboardApiV1DashboardsDashboardIdSharePost_0**
> any shareDashboardApiV1DashboardsDashboardIdSharePost_0(shareDashboardRequest)

Share a dashboard with other users.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    ShareDashboardRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let shareDashboardRequest: ShareDashboardRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.shareDashboardApiV1DashboardsDashboardIdSharePost_0(
    dashboardId,
    shareDashboardRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **shareDashboardRequest** | **ShareDashboardRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **updateDashboardApiV1DashboardsDashboardIdPut**
> DashboardResponse updateDashboardApiV1DashboardsDashboardIdPut(updateDashboardRequest)

Update a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    UpdateDashboardRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let updateDashboardRequest: UpdateDashboardRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateDashboardApiV1DashboardsDashboardIdPut(
    dashboardId,
    updateDashboardRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateDashboardRequest** | **UpdateDashboardRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardResponse**

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

# **updateDashboardApiV1DashboardsDashboardIdPut_0**
> DashboardResponse updateDashboardApiV1DashboardsDashboardIdPut_0(updateDashboardRequest)

Update a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    UpdateDashboardRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let updateDashboardRequest: UpdateDashboardRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateDashboardApiV1DashboardsDashboardIdPut_0(
    dashboardId,
    updateDashboardRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateDashboardRequest** | **UpdateDashboardRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardResponse**

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

# **updateDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdPut**
> any updateDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdPut(dashboardFilterRequest)

Update an existing filter on a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    DashboardFilterRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let filterId: string; // (default to undefined)
let dashboardFilterRequest: DashboardFilterRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdPut(
    dashboardId,
    filterId,
    dashboardFilterRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardFilterRequest** | **DashboardFilterRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **filterId** | [**string**] |  | defaults to undefined|
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

# **updateDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdPut_0**
> any updateDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdPut_0(dashboardFilterRequest)

Update an existing filter on a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    DashboardFilterRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let filterId: string; // (default to undefined)
let dashboardFilterRequest: DashboardFilterRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateDashboardFilterApiV1DashboardsDashboardIdFiltersFilterIdPut_0(
    dashboardId,
    filterId,
    dashboardFilterRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dashboardFilterRequest** | **DashboardFilterRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **filterId** | [**string**] |  | defaults to undefined|
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

# **updateWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdPut**
> any updateWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdPut(addWidgetRequest)

Update a widget.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    AddWidgetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let widgetId: string; // (default to undefined)
let addWidgetRequest: AddWidgetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdPut(
    dashboardId,
    widgetId,
    addWidgetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **addWidgetRequest** | **AddWidgetRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **widgetId** | [**string**] |  | defaults to undefined|
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

# **updateWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdPut_0**
> any updateWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdPut_0(addWidgetRequest)

Update a widget.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    AddWidgetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let widgetId: string; // (default to undefined)
let addWidgetRequest: AddWidgetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateWidgetApiV1DashboardsDashboardIdWidgetsWidgetIdPut_0(
    dashboardId,
    widgetId,
    addWidgetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **addWidgetRequest** | **AddWidgetRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
| **widgetId** | [**string**] |  | defaults to undefined|
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

# **updateWidgetLayoutApiV1DashboardsDashboardIdLayoutPut**
> any updateWidgetLayoutApiV1DashboardsDashboardIdLayoutPut(updateLayoutRequest)

Update widget layout positions for all widgets in a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    UpdateLayoutRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let updateLayoutRequest: UpdateLayoutRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateWidgetLayoutApiV1DashboardsDashboardIdLayoutPut(
    dashboardId,
    updateLayoutRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateLayoutRequest** | **UpdateLayoutRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

# **updateWidgetLayoutApiV1DashboardsDashboardIdLayoutPut_0**
> any updateWidgetLayoutApiV1DashboardsDashboardIdLayoutPut_0(updateLayoutRequest)

Update widget layout positions for all widgets in a dashboard.

### Example

```typescript
import {
    DashboardsApi,
    Configuration,
    UpdateLayoutRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardsApi(configuration);

let dashboardId: string; // (default to undefined)
let updateLayoutRequest: UpdateLayoutRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateWidgetLayoutApiV1DashboardsDashboardIdLayoutPut_0(
    dashboardId,
    updateLayoutRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateLayoutRequest** | **UpdateLayoutRequest**|  | |
| **dashboardId** | [**string**] |  | defaults to undefined|
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

