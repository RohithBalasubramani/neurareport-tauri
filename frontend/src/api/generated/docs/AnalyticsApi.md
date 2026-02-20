# AnalyticsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdPost**](#addfavoriteapiv1analyticsfavoritesentitytypeentityidpost) | **POST** /api/v1/analytics/favorites/{entity_type}/{entity_id} | Add Favorite|
|[**analyzeCorrelationsApiV1AnalyticsCorrelationsPost**](#analyzecorrelationsapiv1analyticscorrelationspost) | **POST** /api/v1/analytics/correlations | Analyze Correlations|
|[**analyzeTrendsApiV1AnalyticsTrendsPost**](#analyzetrendsapiv1analyticstrendspost) | **POST** /api/v1/analytics/trends | Analyze Trends|
|[**bulkAddTagsApiV1AnalyticsBulkTemplatesAddTagsPost**](#bulkaddtagsapiv1analyticsbulktemplatesaddtagspost) | **POST** /api/v1/analytics/bulk/templates/add-tags | Bulk Add Tags|
|[**bulkCancelJobsApiV1AnalyticsBulkJobsCancelPost**](#bulkcanceljobsapiv1analyticsbulkjobscancelpost) | **POST** /api/v1/analytics/bulk/jobs/cancel | Bulk Cancel Jobs|
|[**bulkDeleteJobsApiV1AnalyticsBulkJobsDeletePost**](#bulkdeletejobsapiv1analyticsbulkjobsdeletepost) | **POST** /api/v1/analytics/bulk/jobs/delete | Bulk Delete Jobs|
|[**bulkDeleteTemplatesApiV1AnalyticsBulkTemplatesDeletePost**](#bulkdeletetemplatesapiv1analyticsbulktemplatesdeletepost) | **POST** /api/v1/analytics/bulk/templates/delete | Bulk Delete Templates|
|[**bulkUpdateTemplateStatusApiV1AnalyticsBulkTemplatesUpdateStatusPost**](#bulkupdatetemplatestatusapiv1analyticsbulktemplatesupdatestatuspost) | **POST** /api/v1/analytics/bulk/templates/update-status | Bulk Update Template Status|
|[**checkFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdGet**](#checkfavoriteapiv1analyticsfavoritesentitytypeentityidget) | **GET** /api/v1/analytics/favorites/{entity_type}/{entity_id} | Check Favorite|
|[**clearActivityLogApiV1AnalyticsActivityDelete**](#clearactivitylogapiv1analyticsactivitydelete) | **DELETE** /api/v1/analytics/activity | Clear Activity Log|
|[**clearAllNotificationsApiV1AnalyticsNotificationsDelete**](#clearallnotificationsapiv1analyticsnotificationsdelete) | **DELETE** /api/v1/analytics/notifications | Clear All Notifications|
|[**createNotificationApiV1AnalyticsNotificationsPost**](#createnotificationapiv1analyticsnotificationspost) | **POST** /api/v1/analytics/notifications | Create Notification|
|[**deleteNotificationApiV1AnalyticsNotificationsNotificationIdDelete**](#deletenotificationapiv1analyticsnotificationsnotificationiddelete) | **DELETE** /api/v1/analytics/notifications/{notification_id} | Delete Notification|
|[**detectAnomaliesApiV1AnalyticsAnomaliesPost**](#detectanomaliesapiv1analyticsanomaliespost) | **POST** /api/v1/analytics/anomalies | Detect Anomalies|
|[**exportConfigurationApiV1AnalyticsExportConfigGet**](#exportconfigurationapiv1analyticsexportconfigget) | **GET** /api/v1/analytics/export/config | Export Configuration|
|[**generateInsightsApiV1AnalyticsInsightsPost**](#generateinsightsapiv1analyticsinsightspost) | **POST** /api/v1/analytics/insights | Generate Insights|
|[**getActivityLogApiV1AnalyticsActivityGet**](#getactivitylogapiv1analyticsactivityget) | **GET** /api/v1/analytics/activity | Get Activity Log|
|[**getDashboardAnalyticsApiV1AnalyticsDashboardGet**](#getdashboardanalyticsapiv1analyticsdashboardget) | **GET** /api/v1/analytics/dashboard | Get Dashboard Analytics|
|[**getFavoritesApiV1AnalyticsFavoritesGet**](#getfavoritesapiv1analyticsfavoritesget) | **GET** /api/v1/analytics/favorites | Get Favorites|
|[**getNotificationsApiV1AnalyticsNotificationsGet**](#getnotificationsapiv1analyticsnotificationsget) | **GET** /api/v1/analytics/notifications | Get Notifications|
|[**getPreferencesApiV1AnalyticsPreferencesGet**](#getpreferencesapiv1analyticspreferencesget) | **GET** /api/v1/analytics/preferences | Get Preferences|
|[**getReportHistoryApiV1AnalyticsReportsHistoryGet**](#getreporthistoryapiv1analyticsreportshistoryget) | **GET** /api/v1/analytics/reports/history | Get Report History|
|[**getUnreadCountApiV1AnalyticsNotificationsUnreadCountGet**](#getunreadcountapiv1analyticsnotificationsunreadcountget) | **GET** /api/v1/analytics/notifications/unread-count | Get Unread Count|
|[**getUsageStatisticsApiV1AnalyticsUsageGet**](#getusagestatisticsapiv1analyticsusageget) | **GET** /api/v1/analytics/usage | Get Usage Statistics|
|[**globalSearchApiV1AnalyticsSearchGet**](#globalsearchapiv1analyticssearchget) | **GET** /api/v1/analytics/search | Global Search|
|[**logActivityApiV1AnalyticsActivityPost**](#logactivityapiv1analyticsactivitypost) | **POST** /api/v1/analytics/activity | Log Activity|
|[**markAllReadApiV1AnalyticsNotificationsReadAllPut**](#markallreadapiv1analyticsnotificationsreadallput) | **PUT** /api/v1/analytics/notifications/read-all | Mark All Read|
|[**markNotificationReadApiV1AnalyticsNotificationsNotificationIdReadPut**](#marknotificationreadapiv1analyticsnotificationsnotificationidreadput) | **PUT** /api/v1/analytics/notifications/{notification_id}/read | Mark Notification Read|
|[**removeFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdDelete**](#removefavoriteapiv1analyticsfavoritesentitytypeentityiddelete) | **DELETE** /api/v1/analytics/favorites/{entity_type}/{entity_id} | Remove Favorite|
|[**setPreferenceApiV1AnalyticsPreferencesKeyPut**](#setpreferenceapiv1analyticspreferenceskeyput) | **PUT** /api/v1/analytics/preferences/{key} | Set Preference|
|[**updatePreferencesApiV1AnalyticsPreferencesPut**](#updatepreferencesapiv1analyticspreferencesput) | **PUT** /api/v1/analytics/preferences | Update Preferences|
|[**whatIfAnalysisApiV1AnalyticsWhatifPost**](#whatifanalysisapiv1analyticswhatifpost) | **POST** /api/v1/analytics/whatif | What If Analysis|

# **addFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdPost**
> { [key: string]: any; } addFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdPost()

Add an item to favorites.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let entityType: string; // (default to undefined)
let entityId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdPost(
    entityType,
    entityId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **entityType** | [**string**] |  | defaults to undefined|
| **entityId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **analyzeCorrelationsApiV1AnalyticsCorrelationsPost**
> CorrelationsResponse analyzeCorrelationsApiV1AnalyticsCorrelationsPost(correlationsRequest)

Analyze correlations between data series.  Calculates Pearson, Spearman, or Kendall correlation coefficients between all pairs of variables.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    CorrelationsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let correlationsRequest: CorrelationsRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.analyzeCorrelationsApiV1AnalyticsCorrelationsPost(
    correlationsRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **correlationsRequest** | **CorrelationsRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CorrelationsResponse**

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

# **analyzeTrendsApiV1AnalyticsTrendsPost**
> TrendResponse analyzeTrendsApiV1AnalyticsTrendsPost(trendRequest)

Analyze trends and generate forecasts.  Uses linear regression, exponential smoothing, ARIMA, or Prophet to detect trends and forecast future values.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    TrendRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let trendRequest: TrendRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.analyzeTrendsApiV1AnalyticsTrendsPost(
    trendRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trendRequest** | **TrendRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrendResponse**

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

# **bulkAddTagsApiV1AnalyticsBulkTemplatesAddTagsPost**
> { [key: string]: any; } bulkAddTagsApiV1AnalyticsBulkTemplatesAddTagsPost(bulkTemplateRequest)

Add tags to multiple templates.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    BulkTemplateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let bulkTemplateRequest: BulkTemplateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkAddTagsApiV1AnalyticsBulkTemplatesAddTagsPost(
    bulkTemplateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bulkTemplateRequest** | **BulkTemplateRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **bulkCancelJobsApiV1AnalyticsBulkJobsCancelPost**
> { [key: string]: any; } bulkCancelJobsApiV1AnalyticsBulkJobsCancelPost(bulkJobRequest)

Cancel multiple jobs.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    BulkJobRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let bulkJobRequest: BulkJobRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkCancelJobsApiV1AnalyticsBulkJobsCancelPost(
    bulkJobRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bulkJobRequest** | **BulkJobRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **bulkDeleteJobsApiV1AnalyticsBulkJobsDeletePost**
> { [key: string]: any; } bulkDeleteJobsApiV1AnalyticsBulkJobsDeletePost(bulkJobRequest)

Delete multiple jobs from history.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    BulkJobRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let bulkJobRequest: BulkJobRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkDeleteJobsApiV1AnalyticsBulkJobsDeletePost(
    bulkJobRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bulkJobRequest** | **BulkJobRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **bulkDeleteTemplatesApiV1AnalyticsBulkTemplatesDeletePost**
> { [key: string]: any; } bulkDeleteTemplatesApiV1AnalyticsBulkTemplatesDeletePost(bulkTemplateRequest)

Delete multiple templates in bulk.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    BulkTemplateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let bulkTemplateRequest: BulkTemplateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkDeleteTemplatesApiV1AnalyticsBulkTemplatesDeletePost(
    bulkTemplateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bulkTemplateRequest** | **BulkTemplateRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **bulkUpdateTemplateStatusApiV1AnalyticsBulkTemplatesUpdateStatusPost**
> { [key: string]: any; } bulkUpdateTemplateStatusApiV1AnalyticsBulkTemplatesUpdateStatusPost(bulkTemplateRequest)

Update status for multiple templates.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    BulkTemplateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let bulkTemplateRequest: BulkTemplateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkUpdateTemplateStatusApiV1AnalyticsBulkTemplatesUpdateStatusPost(
    bulkTemplateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bulkTemplateRequest** | **BulkTemplateRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **checkFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdGet**
> { [key: string]: any; } checkFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdGet()

Check if an item is a favorite.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let entityType: string; // (default to undefined)
let entityId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdGet(
    entityType,
    entityId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **entityType** | [**string**] |  | defaults to undefined|
| **entityId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **clearActivityLogApiV1AnalyticsActivityDelete**
> { [key: string]: any; } clearActivityLogApiV1AnalyticsActivityDelete()

Clear all activity log entries. Requires X-Confirm-Destructive: true header.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let xConfirmDestructive: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.clearActivityLogApiV1AnalyticsActivityDelete(
    xConfirmDestructive,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xConfirmDestructive** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **clearAllNotificationsApiV1AnalyticsNotificationsDelete**
> { [key: string]: any; } clearAllNotificationsApiV1AnalyticsNotificationsDelete()

Clear all notifications. Requires X-Confirm-Destructive: true header.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let xConfirmDestructive: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.clearAllNotificationsApiV1AnalyticsNotificationsDelete(
    xConfirmDestructive,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xConfirmDestructive** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **createNotificationApiV1AnalyticsNotificationsPost**
> { [key: string]: any; } createNotificationApiV1AnalyticsNotificationsPost(createNotificationRequest)

Create a new notification.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    CreateNotificationRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let createNotificationRequest: CreateNotificationRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createNotificationApiV1AnalyticsNotificationsPost(
    createNotificationRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createNotificationRequest** | **CreateNotificationRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **deleteNotificationApiV1AnalyticsNotificationsNotificationIdDelete**
> { [key: string]: any; } deleteNotificationApiV1AnalyticsNotificationsNotificationIdDelete()

Delete a notification.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let notificationId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteNotificationApiV1AnalyticsNotificationsNotificationIdDelete(
    notificationId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **notificationId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **detectAnomaliesApiV1AnalyticsAnomaliesPost**
> AnomaliesResponse detectAnomaliesApiV1AnalyticsAnomaliesPost(anomaliesRequest)

Detect anomalies in data.  Uses statistical methods to identify point anomalies, contextual anomalies, and collective anomalies.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    AnomaliesRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let anomaliesRequest: AnomaliesRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.detectAnomaliesApiV1AnalyticsAnomaliesPost(
    anomaliesRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **anomaliesRequest** | **AnomaliesRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AnomaliesResponse**

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

# **exportConfigurationApiV1AnalyticsExportConfigGet**
> { [key: string]: any; } exportConfigurationApiV1AnalyticsExportConfigGet()

Export all configuration (templates, connections, schedules, preferences) as JSON.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportConfigurationApiV1AnalyticsExportConfigGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **generateInsightsApiV1AnalyticsInsightsPost**
> InsightsResponse generateInsightsApiV1AnalyticsInsightsPost(insightsRequest)

Generate automated insights from data.  Analyzes data series to discover trends, anomalies, distributions, and other notable patterns.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    InsightsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let insightsRequest: InsightsRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateInsightsApiV1AnalyticsInsightsPost(
    insightsRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **insightsRequest** | **InsightsRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**InsightsResponse**

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

# **getActivityLogApiV1AnalyticsActivityGet**
> { [key: string]: any; } getActivityLogApiV1AnalyticsActivityGet()

Get the activity log with optional filtering.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let entityType: string; // (optional) (default to undefined)
let action: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getActivityLogApiV1AnalyticsActivityGet(
    limit,
    offset,
    entityType,
    action,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **entityType** | [**string**] |  | (optional) defaults to undefined|
| **action** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **getDashboardAnalyticsApiV1AnalyticsDashboardGet**
> { [key: string]: any; } getDashboardAnalyticsApiV1AnalyticsDashboardGet()

Get comprehensive dashboard analytics.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDashboardAnalyticsApiV1AnalyticsDashboardGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **getFavoritesApiV1AnalyticsFavoritesGet**
> { [key: string]: any; } getFavoritesApiV1AnalyticsFavoritesGet()

Get all favorites.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getFavoritesApiV1AnalyticsFavoritesGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **getNotificationsApiV1AnalyticsNotificationsGet**
> { [key: string]: any; } getNotificationsApiV1AnalyticsNotificationsGet()

Get notifications list.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let limit: number; // (optional) (default to 50)
let unreadOnly: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getNotificationsApiV1AnalyticsNotificationsGet(
    limit,
    unreadOnly,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **unreadOnly** | [**boolean**] |  | (optional) defaults to false|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **getPreferencesApiV1AnalyticsPreferencesGet**
> { [key: string]: any; } getPreferencesApiV1AnalyticsPreferencesGet()

Get user preferences.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPreferencesApiV1AnalyticsPreferencesGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **getReportHistoryApiV1AnalyticsReportsHistoryGet**
> { [key: string]: any; } getReportHistoryApiV1AnalyticsReportsHistoryGet()

Get report generation history with filtering.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let status: string; // (optional) (default to undefined)
let templateId: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getReportHistoryApiV1AnalyticsReportsHistoryGet(
    limit,
    offset,
    status,
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **status** | [**string**] |  | (optional) defaults to undefined|
| **templateId** | [**string**] |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **getUnreadCountApiV1AnalyticsNotificationsUnreadCountGet**
> { [key: string]: number; } getUnreadCountApiV1AnalyticsNotificationsUnreadCountGet()

Get count of unread notifications.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getUnreadCountApiV1AnalyticsNotificationsUnreadCountGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: number; }**

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

# **getUsageStatisticsApiV1AnalyticsUsageGet**
> { [key: string]: any; } getUsageStatisticsApiV1AnalyticsUsageGet()

Get detailed usage statistics over time.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let period: string; // (optional) (default to 'week')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getUsageStatisticsApiV1AnalyticsUsageGet(
    period,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **period** | [**string**] |  | (optional) defaults to 'week'|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **globalSearchApiV1AnalyticsSearchGet**
> { [key: string]: any; } globalSearchApiV1AnalyticsSearchGet()

Search across templates, connections, and jobs.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let q: string; // (default to undefined)
let types: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 20)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.globalSearchApiV1AnalyticsSearchGet(
    q,
    types,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **q** | [**string**] |  | defaults to undefined|
| **types** | [**string**] |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 20|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **logActivityApiV1AnalyticsActivityPost**
> { [key: string]: any; } logActivityApiV1AnalyticsActivityPost(logActivityRequest)

Log an activity event.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    LogActivityRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let logActivityRequest: LogActivityRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.logActivityApiV1AnalyticsActivityPost(
    logActivityRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **logActivityRequest** | **LogActivityRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **markAllReadApiV1AnalyticsNotificationsReadAllPut**
> { [key: string]: any; } markAllReadApiV1AnalyticsNotificationsReadAllPut()

Mark all notifications as read.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.markAllReadApiV1AnalyticsNotificationsReadAllPut(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **markNotificationReadApiV1AnalyticsNotificationsNotificationIdReadPut**
> { [key: string]: any; } markNotificationReadApiV1AnalyticsNotificationsNotificationIdReadPut()

Mark a notification as read.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let notificationId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.markNotificationReadApiV1AnalyticsNotificationsNotificationIdReadPut(
    notificationId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **notificationId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **removeFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdDelete**
> { [key: string]: any; } removeFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdDelete()

Remove an item from favorites.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let entityType: string; // (default to undefined)
let entityId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeFavoriteApiV1AnalyticsFavoritesEntityTypeEntityIdDelete(
    entityType,
    entityId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **entityType** | [**string**] |  | defaults to undefined|
| **entityId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **setPreferenceApiV1AnalyticsPreferencesKeyPut**
> { [key: string]: any; } setPreferenceApiV1AnalyticsPreferencesKeyPut()

Set a single user preference.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    PreferenceValue
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let key: string; // (default to undefined)
let value: any; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let preferenceValue: PreferenceValue; // (optional)

const { status, data } = await apiInstance.setPreferenceApiV1AnalyticsPreferencesKeyPut(
    key,
    value,
    xApiKey,
    preferenceValue
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **preferenceValue** | **PreferenceValue**|  | |
| **key** | [**string**] |  | defaults to undefined|
| **value** | **any** |  | (optional) defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **updatePreferencesApiV1AnalyticsPreferencesPut**
> { [key: string]: any; } updatePreferencesApiV1AnalyticsPreferencesPut(requestBody)

Update user preferences.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let requestBody: { [key: string]: any; }; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePreferencesApiV1AnalyticsPreferencesPut(
    requestBody,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **whatIfAnalysisApiV1AnalyticsWhatifPost**
> WhatIfResponse whatIfAnalysisApiV1AnalyticsWhatifPost(backendAppSchemasAnalyticsAnalyticsWhatIfRequest)

Perform what-if scenario analysis.  Evaluates how changes to input variables might affect a target variable based on historical relationships.

### Example

```typescript
import {
    AnalyticsApi,
    Configuration,
    BackendAppSchemasAnalyticsAnalyticsWhatIfRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let backendAppSchemasAnalyticsAnalyticsWhatIfRequest: BackendAppSchemasAnalyticsAnalyticsWhatIfRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.whatIfAnalysisApiV1AnalyticsWhatifPost(
    backendAppSchemasAnalyticsAnalyticsWhatIfRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasAnalyticsAnalyticsWhatIfRequest** | **BackendAppSchemasAnalyticsAnalyticsWhatIfRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WhatIfResponse**

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

