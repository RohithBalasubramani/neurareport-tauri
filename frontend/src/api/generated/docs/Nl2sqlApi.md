# Nl2sqlApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**deleteQueryHistoryEntryApiV1Nl2sqlHistoryEntryIdDelete**](#deletequeryhistoryentryapiv1nl2sqlhistoryentryiddelete) | **DELETE** /api/v1/nl2sql/history/{entry_id} | Delete Query History Entry|
|[**deleteSavedQueryApiV1Nl2sqlSavedQueryIdDelete**](#deletesavedqueryapiv1nl2sqlsavedqueryiddelete) | **DELETE** /api/v1/nl2sql/saved/{query_id} | Delete Saved Query|
|[**executeQueryApiV1Nl2sqlExecutePost**](#executequeryapiv1nl2sqlexecutepost) | **POST** /api/v1/nl2sql/execute | Execute Query|
|[**explainQueryApiV1Nl2sqlExplainPost**](#explainqueryapiv1nl2sqlexplainpost) | **POST** /api/v1/nl2sql/explain | Explain Query|
|[**generateSqlApiV1Nl2sqlGeneratePost**](#generatesqlapiv1nl2sqlgeneratepost) | **POST** /api/v1/nl2sql/generate | Generate Sql|
|[**getQueryHistoryApiV1Nl2sqlHistoryGet**](#getqueryhistoryapiv1nl2sqlhistoryget) | **GET** /api/v1/nl2sql/history | Get Query History|
|[**getSavedQueryApiV1Nl2sqlSavedQueryIdGet**](#getsavedqueryapiv1nl2sqlsavedqueryidget) | **GET** /api/v1/nl2sql/saved/{query_id} | Get Saved Query|
|[**listSavedQueriesApiV1Nl2sqlSavedGet**](#listsavedqueriesapiv1nl2sqlsavedget) | **GET** /api/v1/nl2sql/saved | List Saved Queries|
|[**saveQueryApiV1Nl2sqlSavePost**](#savequeryapiv1nl2sqlsavepost) | **POST** /api/v1/nl2sql/save | Save Query|

# **deleteQueryHistoryEntryApiV1Nl2sqlHistoryEntryIdDelete**
> any deleteQueryHistoryEntryApiV1Nl2sqlHistoryEntryIdDelete()

Delete a query history entry.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let entryId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteQueryHistoryEntryApiV1Nl2sqlHistoryEntryIdDelete(
    entryId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **entryId** | [**string**] |  | defaults to undefined|
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

# **deleteSavedQueryApiV1Nl2sqlSavedQueryIdDelete**
> any deleteSavedQueryApiV1Nl2sqlSavedQueryIdDelete()

Delete a saved query.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let queryId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSavedQueryApiV1Nl2sqlSavedQueryIdDelete(
    queryId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **queryId** | [**string**] |  | defaults to undefined|
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

# **executeQueryApiV1Nl2sqlExecutePost**
> any executeQueryApiV1Nl2sqlExecutePost(nL2SQLExecuteRequest)

Execute a SQL query and return results.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration,
    NL2SQLExecuteRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let nL2SQLExecuteRequest: NL2SQLExecuteRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.executeQueryApiV1Nl2sqlExecutePost(
    nL2SQLExecuteRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **nL2SQLExecuteRequest** | **NL2SQLExecuteRequest**|  | |
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

# **explainQueryApiV1Nl2sqlExplainPost**
> any explainQueryApiV1Nl2sqlExplainPost()

Get a natural language explanation of a SQL query.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let sql: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.explainQueryApiV1Nl2sqlExplainPost(
    sql,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sql** | [**string**] |  | defaults to undefined|
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

# **generateSqlApiV1Nl2sqlGeneratePost**
> any generateSqlApiV1Nl2sqlGeneratePost(nL2SQLGenerateRequest)

Generate SQL from a natural language question.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration,
    NL2SQLGenerateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let nL2SQLGenerateRequest: NL2SQLGenerateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateSqlApiV1Nl2sqlGeneratePost(
    nL2SQLGenerateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **nL2SQLGenerateRequest** | **NL2SQLGenerateRequest**|  | |
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

# **getQueryHistoryApiV1Nl2sqlHistoryGet**
> any getQueryHistoryApiV1Nl2sqlHistoryGet()

Get query history.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let connectionId: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getQueryHistoryApiV1Nl2sqlHistoryGet(
    connectionId,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|
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

# **getSavedQueryApiV1Nl2sqlSavedQueryIdGet**
> any getSavedQueryApiV1Nl2sqlSavedQueryIdGet()

Get a saved query by ID.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let queryId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSavedQueryApiV1Nl2sqlSavedQueryIdGet(
    queryId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **queryId** | [**string**] |  | defaults to undefined|
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

# **listSavedQueriesApiV1Nl2sqlSavedGet**
> any listSavedQueriesApiV1Nl2sqlSavedGet()

List saved queries.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let connectionId: string; // (optional) (default to undefined)
let tags: Array<string>; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSavedQueriesApiV1Nl2sqlSavedGet(
    connectionId,
    tags,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|
| **tags** | **Array&lt;string&gt;** |  | (optional) defaults to undefined|
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

# **saveQueryApiV1Nl2sqlSavePost**
> any saveQueryApiV1Nl2sqlSavePost(nL2SQLSaveRequest)

Save a query as a reusable data source.

### Example

```typescript
import {
    Nl2sqlApi,
    Configuration,
    NL2SQLSaveRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new Nl2sqlApi(configuration);

let nL2SQLSaveRequest: NL2SQLSaveRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.saveQueryApiV1Nl2sqlSavePost(
    nL2SQLSaveRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **nL2SQLSaveRequest** | **NL2SQLSaveRequest**|  | |
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

