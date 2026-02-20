# ConnectorsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**checkConnectionHealthApiV1ConnectorsConnectionIdHealthPost**](#checkconnectionhealthapiv1connectorsconnectionidhealthpost) | **POST** /api/v1/connectors/{connection_id}/health | Check Connection Health|
|[**checkConnectionHealthApiV1ConnectorsConnectionIdHealthPost_0**](#checkconnectionhealthapiv1connectorsconnectionidhealthpost_0) | **POST** /api/v1/connectors/{connection_id}/health | Check Connection Health|
|[**createConnectionApiV1ConnectorsConnectorTypeConnectPost**](#createconnectionapiv1connectorsconnectortypeconnectpost) | **POST** /api/v1/connectors/{connector_type}/connect | Create Connection|
|[**createConnectionApiV1ConnectorsConnectorTypeConnectPost_0**](#createconnectionapiv1connectorsconnectortypeconnectpost_0) | **POST** /api/v1/connectors/{connector_type}/connect | Create Connection|
|[**deleteConnectionApiV1ConnectorsConnectionIdDelete**](#deleteconnectionapiv1connectorsconnectioniddelete) | **DELETE** /api/v1/connectors/{connection_id} | Delete Connection|
|[**deleteConnectionApiV1ConnectorsConnectionIdDelete_0**](#deleteconnectionapiv1connectorsconnectioniddelete_0) | **DELETE** /api/v1/connectors/{connection_id} | Delete Connection|
|[**downloadConnectionFileApiV1ConnectorsConnectionIdFilesDownloadGet**](#downloadconnectionfileapiv1connectorsconnectionidfilesdownloadget) | **GET** /api/v1/connectors/{connection_id}/files/download | Download Connection File|
|[**downloadConnectionFileApiV1ConnectorsConnectionIdFilesDownloadGet_0**](#downloadconnectionfileapiv1connectorsconnectionidfilesdownloadget_0) | **GET** /api/v1/connectors/{connection_id}/files/download | Download Connection File|
|[**executeQueryApiV1ConnectorsConnectionIdQueryPost**](#executequeryapiv1connectorsconnectionidquerypost) | **POST** /api/v1/connectors/{connection_id}/query | Execute Query|
|[**executeQueryApiV1ConnectorsConnectionIdQueryPost_0**](#executequeryapiv1connectorsconnectionidquerypost_0) | **POST** /api/v1/connectors/{connection_id}/query | Execute Query|
|[**getConnectionApiV1ConnectorsConnectionIdGet**](#getconnectionapiv1connectorsconnectionidget) | **GET** /api/v1/connectors/{connection_id} | Get Connection|
|[**getConnectionApiV1ConnectorsConnectionIdGet_0**](#getconnectionapiv1connectorsconnectionidget_0) | **GET** /api/v1/connectors/{connection_id} | Get Connection|
|[**getConnectionSchemaApiV1ConnectorsConnectionIdSchemaGet**](#getconnectionschemaapiv1connectorsconnectionidschemaget) | **GET** /api/v1/connectors/{connection_id}/schema | Get Connection Schema|
|[**getConnectionSchemaApiV1ConnectorsConnectionIdSchemaGet_0**](#getconnectionschemaapiv1connectorsconnectionidschemaget_0) | **GET** /api/v1/connectors/{connection_id}/schema | Get Connection Schema|
|[**getConnectorTypeApiV1ConnectorsTypesConnectorTypeGet**](#getconnectortypeapiv1connectorstypesconnectortypeget) | **GET** /api/v1/connectors/types/{connector_type} | Get Connector Type|
|[**getConnectorTypeApiV1ConnectorsTypesConnectorTypeGet_0**](#getconnectortypeapiv1connectorstypesconnectortypeget_0) | **GET** /api/v1/connectors/types/{connector_type} | Get Connector Type|
|[**getOauthUrlApiV1ConnectorsConnectorTypeOauthAuthorizeGet**](#getoauthurlapiv1connectorsconnectortypeoauthauthorizeget) | **GET** /api/v1/connectors/{connector_type}/oauth/authorize | Get Oauth Url|
|[**getOauthUrlApiV1ConnectorsConnectorTypeOauthAuthorizeGet_0**](#getoauthurlapiv1connectorsconnectortypeoauthauthorizeget_0) | **GET** /api/v1/connectors/{connector_type}/oauth/authorize | Get Oauth Url|
|[**getSyncStatusApiV1ConnectorsConnectionIdSyncStatusGet**](#getsyncstatusapiv1connectorsconnectionidsyncstatusget) | **GET** /api/v1/connectors/{connection_id}/sync/status | Get Sync Status|
|[**getSyncStatusApiV1ConnectorsConnectionIdSyncStatusGet_0**](#getsyncstatusapiv1connectorsconnectionidsyncstatusget_0) | **GET** /api/v1/connectors/{connection_id}/sync/status | Get Sync Status|
|[**handleOauthCallbackApiV1ConnectorsConnectorTypeOauthCallbackPost**](#handleoauthcallbackapiv1connectorsconnectortypeoauthcallbackpost) | **POST** /api/v1/connectors/{connector_type}/oauth/callback | Handle Oauth Callback|
|[**handleOauthCallbackApiV1ConnectorsConnectorTypeOauthCallbackPost_0**](#handleoauthcallbackapiv1connectorsconnectortypeoauthcallbackpost_0) | **POST** /api/v1/connectors/{connector_type}/oauth/callback | Handle Oauth Callback|
|[**listConnectionFilesApiV1ConnectorsConnectionIdFilesGet**](#listconnectionfilesapiv1connectorsconnectionidfilesget) | **GET** /api/v1/connectors/{connection_id}/files | List Connection Files|
|[**listConnectionFilesApiV1ConnectorsConnectionIdFilesGet_0**](#listconnectionfilesapiv1connectorsconnectionidfilesget_0) | **GET** /api/v1/connectors/{connection_id}/files | List Connection Files|
|[**listConnectionsApiV1ConnectorsGet**](#listconnectionsapiv1connectorsget) | **GET** /api/v1/connectors | List Connections|
|[**listConnectionsApiV1ConnectorsGet_0**](#listconnectionsapiv1connectorsget_0) | **GET** /api/v1/connectors | List Connections|
|[**listConnectorTypesApiV1ConnectorsTypesGet**](#listconnectortypesapiv1connectorstypesget) | **GET** /api/v1/connectors/types | List Connector Types|
|[**listConnectorTypesApiV1ConnectorsTypesGet_0**](#listconnectortypesapiv1connectorstypesget_0) | **GET** /api/v1/connectors/types | List Connector Types|
|[**listConnectorsByCategoryApiV1ConnectorsTypesByCategoryCategoryGet**](#listconnectorsbycategoryapiv1connectorstypesbycategorycategoryget) | **GET** /api/v1/connectors/types/by-category/{category} | List Connectors By Category|
|[**listConnectorsByCategoryApiV1ConnectorsTypesByCategoryCategoryGet_0**](#listconnectorsbycategoryapiv1connectorstypesbycategorycategoryget_0) | **GET** /api/v1/connectors/types/by-category/{category} | List Connectors By Category|
|[**scheduleConnectionSyncApiV1ConnectorsConnectionIdSyncSchedulePost**](#scheduleconnectionsyncapiv1connectorsconnectionidsyncschedulepost) | **POST** /api/v1/connectors/{connection_id}/sync/schedule | Schedule Connection Sync|
|[**scheduleConnectionSyncApiV1ConnectorsConnectionIdSyncSchedulePost_0**](#scheduleconnectionsyncapiv1connectorsconnectionidsyncschedulepost_0) | **POST** /api/v1/connectors/{connection_id}/sync/schedule | Schedule Connection Sync|
|[**startConnectionSyncApiV1ConnectorsConnectionIdSyncPost**](#startconnectionsyncapiv1connectorsconnectionidsyncpost) | **POST** /api/v1/connectors/{connection_id}/sync | Start Connection Sync|
|[**startConnectionSyncApiV1ConnectorsConnectionIdSyncPost_0**](#startconnectionsyncapiv1connectorsconnectionidsyncpost_0) | **POST** /api/v1/connectors/{connection_id}/sync | Start Connection Sync|
|[**testConnectionApiV1ConnectorsConnectorTypeTestPost**](#testconnectionapiv1connectorsconnectortypetestpost) | **POST** /api/v1/connectors/{connector_type}/test | Test Connection|
|[**testConnectionApiV1ConnectorsConnectorTypeTestPost_0**](#testconnectionapiv1connectorsconnectortypetestpost_0) | **POST** /api/v1/connectors/{connector_type}/test | Test Connection|
|[**uploadConnectionFileApiV1ConnectorsConnectionIdFilesUploadPost**](#uploadconnectionfileapiv1connectorsconnectionidfilesuploadpost) | **POST** /api/v1/connectors/{connection_id}/files/upload | Upload Connection File|
|[**uploadConnectionFileApiV1ConnectorsConnectionIdFilesUploadPost_0**](#uploadconnectionfileapiv1connectorsconnectionidfilesuploadpost_0) | **POST** /api/v1/connectors/{connection_id}/files/upload | Upload Connection File|

# **checkConnectionHealthApiV1ConnectorsConnectionIdHealthPost**
> TestConnectionResponse checkConnectionHealthApiV1ConnectorsConnectionIdHealthPost()

Check if a connection is healthy.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkConnectionHealthApiV1ConnectorsConnectionIdHealthPost(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TestConnectionResponse**

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

# **checkConnectionHealthApiV1ConnectorsConnectionIdHealthPost_0**
> TestConnectionResponse checkConnectionHealthApiV1ConnectorsConnectionIdHealthPost_0()

Check if a connection is healthy.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkConnectionHealthApiV1ConnectorsConnectionIdHealthPost_0(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TestConnectionResponse**

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

# **createConnectionApiV1ConnectorsConnectorTypeConnectPost**
> ConnectionResponse createConnectionApiV1ConnectorsConnectorTypeConnectPost(createConnectionRequest)

Create and save a new connection.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration,
    CreateConnectionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let createConnectionRequest: CreateConnectionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createConnectionApiV1ConnectorsConnectorTypeConnectPost(
    connectorType,
    createConnectionRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createConnectionRequest** | **CreateConnectionRequest**|  | |
| **connectorType** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ConnectionResponse**

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

# **createConnectionApiV1ConnectorsConnectorTypeConnectPost_0**
> ConnectionResponse createConnectionApiV1ConnectorsConnectorTypeConnectPost_0(createConnectionRequest)

Create and save a new connection.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration,
    CreateConnectionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let createConnectionRequest: CreateConnectionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createConnectionApiV1ConnectorsConnectorTypeConnectPost_0(
    connectorType,
    createConnectionRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createConnectionRequest** | **CreateConnectionRequest**|  | |
| **connectorType** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ConnectionResponse**

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

# **deleteConnectionApiV1ConnectorsConnectionIdDelete**
> any deleteConnectionApiV1ConnectorsConnectionIdDelete()

Delete a connection.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteConnectionApiV1ConnectorsConnectionIdDelete(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
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

# **deleteConnectionApiV1ConnectorsConnectionIdDelete_0**
> any deleteConnectionApiV1ConnectorsConnectionIdDelete_0()

Delete a connection.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteConnectionApiV1ConnectorsConnectionIdDelete_0(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
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

# **downloadConnectionFileApiV1ConnectorsConnectionIdFilesDownloadGet**
> any downloadConnectionFileApiV1ConnectorsConnectionIdFilesDownloadGet()

Download a file from a cloud storage connection.  The *path* query parameter identifies the file to download.  The response streams the raw file bytes with an appropriate content type.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let path: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.downloadConnectionFileApiV1ConnectorsConnectionIdFilesDownloadGet(
    connectionId,
    path,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **path** | [**string**] |  | defaults to undefined|
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

# **downloadConnectionFileApiV1ConnectorsConnectionIdFilesDownloadGet_0**
> any downloadConnectionFileApiV1ConnectorsConnectionIdFilesDownloadGet_0()

Download a file from a cloud storage connection.  The *path* query parameter identifies the file to download.  The response streams the raw file bytes with an appropriate content type.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let path: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.downloadConnectionFileApiV1ConnectorsConnectionIdFilesDownloadGet_0(
    connectionId,
    path,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **path** | [**string**] |  | defaults to undefined|
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

# **executeQueryApiV1ConnectorsConnectionIdQueryPost**
> QueryResponse executeQueryApiV1ConnectorsConnectionIdQueryPost(queryRequest)

Execute a query on a connection.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration,
    QueryRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let queryRequest: QueryRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.executeQueryApiV1ConnectorsConnectionIdQueryPost(
    connectionId,
    queryRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **queryRequest** | **QueryRequest**|  | |
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**QueryResponse**

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

# **executeQueryApiV1ConnectorsConnectionIdQueryPost_0**
> QueryResponse executeQueryApiV1ConnectorsConnectionIdQueryPost_0(queryRequest)

Execute a query on a connection.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration,
    QueryRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let queryRequest: QueryRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.executeQueryApiV1ConnectorsConnectionIdQueryPost_0(
    connectionId,
    queryRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **queryRequest** | **QueryRequest**|  | |
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**QueryResponse**

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

# **getConnectionApiV1ConnectorsConnectionIdGet**
> ConnectionResponse getConnectionApiV1ConnectorsConnectionIdGet()

Get a connection by ID.  Note: connection_id is restricted to UUID format to disambiguate from /{connector_type}/... routes which use short alphanumeric names.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getConnectionApiV1ConnectorsConnectionIdGet(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ConnectionResponse**

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

# **getConnectionApiV1ConnectorsConnectionIdGet_0**
> ConnectionResponse getConnectionApiV1ConnectorsConnectionIdGet_0()

Get a connection by ID.  Note: connection_id is restricted to UUID format to disambiguate from /{connector_type}/... routes which use short alphanumeric names.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getConnectionApiV1ConnectorsConnectionIdGet_0(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ConnectionResponse**

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

# **getConnectionSchemaApiV1ConnectorsConnectionIdSchemaGet**
> any getConnectionSchemaApiV1ConnectorsConnectionIdSchemaGet()

Get schema information for a connection.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getConnectionSchemaApiV1ConnectorsConnectionIdSchemaGet(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
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

# **getConnectionSchemaApiV1ConnectorsConnectionIdSchemaGet_0**
> any getConnectionSchemaApiV1ConnectorsConnectionIdSchemaGet_0()

Get schema information for a connection.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getConnectionSchemaApiV1ConnectorsConnectionIdSchemaGet_0(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
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

# **getConnectorTypeApiV1ConnectorsTypesConnectorTypeGet**
> ConnectorInfo getConnectorTypeApiV1ConnectorsTypesConnectorTypeGet()

Get information about a specific connector type.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getConnectorTypeApiV1ConnectorsTypesConnectorTypeGet(
    connectorType,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectorType** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ConnectorInfo**

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

# **getConnectorTypeApiV1ConnectorsTypesConnectorTypeGet_0**
> ConnectorInfo getConnectorTypeApiV1ConnectorsTypesConnectorTypeGet_0()

Get information about a specific connector type.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getConnectorTypeApiV1ConnectorsTypesConnectorTypeGet_0(
    connectorType,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectorType** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ConnectorInfo**

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

# **getOauthUrlApiV1ConnectorsConnectorTypeOauthAuthorizeGet**
> any getOauthUrlApiV1ConnectorsConnectorTypeOauthAuthorizeGet()

Get OAuth authorization URL for a connector.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let redirectUri: string; // (default to undefined)
let state: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOauthUrlApiV1ConnectorsConnectorTypeOauthAuthorizeGet(
    connectorType,
    redirectUri,
    state,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectorType** | [**string**] |  | defaults to undefined|
| **redirectUri** | [**string**] |  | defaults to undefined|
| **state** | [**string**] |  | (optional) defaults to undefined|
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

# **getOauthUrlApiV1ConnectorsConnectorTypeOauthAuthorizeGet_0**
> any getOauthUrlApiV1ConnectorsConnectorTypeOauthAuthorizeGet_0()

Get OAuth authorization URL for a connector.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let redirectUri: string; // (default to undefined)
let state: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOauthUrlApiV1ConnectorsConnectorTypeOauthAuthorizeGet_0(
    connectorType,
    redirectUri,
    state,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectorType** | [**string**] |  | defaults to undefined|
| **redirectUri** | [**string**] |  | defaults to undefined|
| **state** | [**string**] |  | (optional) defaults to undefined|
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

# **getSyncStatusApiV1ConnectorsConnectionIdSyncStatusGet**
> SyncStatusResponse getSyncStatusApiV1ConnectorsConnectionIdSyncStatusGet()

Get the sync status for a connection.  Returns the most recent sync status from the state store.  If no sync has been run yet, a ``never_synced`` status is returned.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSyncStatusApiV1ConnectorsConnectionIdSyncStatusGet(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SyncStatusResponse**

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

# **getSyncStatusApiV1ConnectorsConnectionIdSyncStatusGet_0**
> SyncStatusResponse getSyncStatusApiV1ConnectorsConnectionIdSyncStatusGet_0()

Get the sync status for a connection.  Returns the most recent sync status from the state store.  If no sync has been run yet, a ``never_synced`` status is returned.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSyncStatusApiV1ConnectorsConnectionIdSyncStatusGet_0(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SyncStatusResponse**

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

# **handleOauthCallbackApiV1ConnectorsConnectorTypeOauthCallbackPost**
> any handleOauthCallbackApiV1ConnectorsConnectorTypeOauthCallbackPost()

Handle OAuth callback and exchange code for tokens.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let code: string; // (default to undefined)
let redirectUri: string; // (default to undefined)
let state: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.handleOauthCallbackApiV1ConnectorsConnectorTypeOauthCallbackPost(
    connectorType,
    code,
    redirectUri,
    state,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectorType** | [**string**] |  | defaults to undefined|
| **code** | [**string**] |  | defaults to undefined|
| **redirectUri** | [**string**] |  | defaults to undefined|
| **state** | [**string**] |  | (optional) defaults to undefined|
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

# **handleOauthCallbackApiV1ConnectorsConnectorTypeOauthCallbackPost_0**
> any handleOauthCallbackApiV1ConnectorsConnectorTypeOauthCallbackPost_0()

Handle OAuth callback and exchange code for tokens.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let code: string; // (default to undefined)
let redirectUri: string; // (default to undefined)
let state: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.handleOauthCallbackApiV1ConnectorsConnectorTypeOauthCallbackPost_0(
    connectorType,
    code,
    redirectUri,
    state,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectorType** | [**string**] |  | defaults to undefined|
| **code** | [**string**] |  | defaults to undefined|
| **redirectUri** | [**string**] |  | defaults to undefined|
| **state** | [**string**] |  | (optional) defaults to undefined|
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

# **listConnectionFilesApiV1ConnectorsConnectionIdFilesGet**
> { [key: string]: any; } listConnectionFilesApiV1ConnectorsConnectionIdFilesGet()

List files for a cloud storage connection.  Returns files and folders at the given *path* within the connected cloud storage provider.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let path: string; // (optional) (default to '/')
let recursive: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectionFilesApiV1ConnectorsConnectionIdFilesGet(
    connectionId,
    path,
    recursive,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **path** | [**string**] |  | (optional) defaults to '/'|
| **recursive** | [**boolean**] |  | (optional) defaults to false|
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

# **listConnectionFilesApiV1ConnectorsConnectionIdFilesGet_0**
> { [key: string]: any; } listConnectionFilesApiV1ConnectorsConnectionIdFilesGet_0()

List files for a cloud storage connection.  Returns files and folders at the given *path* within the connected cloud storage provider.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let path: string; // (optional) (default to '/')
let recursive: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectionFilesApiV1ConnectorsConnectionIdFilesGet_0(
    connectionId,
    path,
    recursive,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **path** | [**string**] |  | (optional) defaults to '/'|
| **recursive** | [**boolean**] |  | (optional) defaults to false|
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

# **listConnectionsApiV1ConnectorsGet**
> any listConnectionsApiV1ConnectorsGet()

List saved connections.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectionsApiV1ConnectorsGet(
    connectorType,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectorType** | [**string**] |  | (optional) defaults to undefined|
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

# **listConnectionsApiV1ConnectorsGet_0**
> any listConnectionsApiV1ConnectorsGet_0()

List saved connections.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectionsApiV1ConnectorsGet_0(
    connectorType,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectorType** | [**string**] |  | (optional) defaults to undefined|
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

# **listConnectorTypesApiV1ConnectorsTypesGet**
> Array<ConnectorInfo> listConnectorTypesApiV1ConnectorsTypesGet()

List all available connector types.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectorTypesApiV1ConnectorsTypesGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ConnectorInfo>**

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

# **listConnectorTypesApiV1ConnectorsTypesGet_0**
> Array<ConnectorInfo> listConnectorTypesApiV1ConnectorsTypesGet_0()

List all available connector types.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectorTypesApiV1ConnectorsTypesGet_0(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ConnectorInfo>**

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

# **listConnectorsByCategoryApiV1ConnectorsTypesByCategoryCategoryGet**
> Array<ConnectorInfo> listConnectorsByCategoryApiV1ConnectorsTypesByCategoryCategoryGet()

List connectors by category.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let category: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectorsByCategoryApiV1ConnectorsTypesByCategoryCategoryGet(
    category,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **category** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ConnectorInfo>**

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

# **listConnectorsByCategoryApiV1ConnectorsTypesByCategoryCategoryGet_0**
> Array<ConnectorInfo> listConnectorsByCategoryApiV1ConnectorsTypesByCategoryCategoryGet_0()

List connectors by category.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let category: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectorsByCategoryApiV1ConnectorsTypesByCategoryCategoryGet_0(
    category,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **category** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ConnectorInfo>**

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

# **scheduleConnectionSyncApiV1ConnectorsConnectionIdSyncSchedulePost**
> SyncScheduleResponse scheduleConnectionSyncApiV1ConnectorsConnectionIdSyncSchedulePost(syncScheduleRequest)

Schedule periodic sync for a connection.  Stores the schedule configuration in the state store under ``connector_sync_status`` so that a background worker can pick it up.  The *interval_minutes* field must be between 5 and 1440 (24h).

### Example

```typescript
import {
    ConnectorsApi,
    Configuration,
    SyncScheduleRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let syncScheduleRequest: SyncScheduleRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scheduleConnectionSyncApiV1ConnectorsConnectionIdSyncSchedulePost(
    connectionId,
    syncScheduleRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **syncScheduleRequest** | **SyncScheduleRequest**|  | |
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SyncScheduleResponse**

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

# **scheduleConnectionSyncApiV1ConnectorsConnectionIdSyncSchedulePost_0**
> SyncScheduleResponse scheduleConnectionSyncApiV1ConnectorsConnectionIdSyncSchedulePost_0(syncScheduleRequest)

Schedule periodic sync for a connection.  Stores the schedule configuration in the state store under ``connector_sync_status`` so that a background worker can pick it up.  The *interval_minutes* field must be between 5 and 1440 (24h).

### Example

```typescript
import {
    ConnectorsApi,
    Configuration,
    SyncScheduleRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let syncScheduleRequest: SyncScheduleRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scheduleConnectionSyncApiV1ConnectorsConnectionIdSyncSchedulePost_0(
    connectionId,
    syncScheduleRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **syncScheduleRequest** | **SyncScheduleRequest**|  | |
| **connectionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SyncScheduleResponse**

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

# **startConnectionSyncApiV1ConnectorsConnectionIdSyncPost**
> { [key: string]: any; } startConnectionSyncApiV1ConnectorsConnectionIdSyncPost()

Start syncing a connection.  Initiates a sync operation for the connection and records the sync status in the persistent state store under ``connector_sync_status``.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.startConnectionSyncApiV1ConnectorsConnectionIdSyncPost(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
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

# **startConnectionSyncApiV1ConnectorsConnectionIdSyncPost_0**
> { [key: string]: any; } startConnectionSyncApiV1ConnectorsConnectionIdSyncPost_0()

Start syncing a connection.  Initiates a sync operation for the connection and records the sync status in the persistent state store under ``connector_sync_status``.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.startConnectionSyncApiV1ConnectorsConnectionIdSyncPost_0(
    connectionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
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

# **testConnectionApiV1ConnectorsConnectorTypeTestPost**
> TestConnectionResponse testConnectionApiV1ConnectorsConnectorTypeTestPost(testConnectionRequest)

Test a connection configuration.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration,
    TestConnectionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let testConnectionRequest: TestConnectionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.testConnectionApiV1ConnectorsConnectorTypeTestPost(
    connectorType,
    testConnectionRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testConnectionRequest** | **TestConnectionRequest**|  | |
| **connectorType** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TestConnectionResponse**

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

# **testConnectionApiV1ConnectorsConnectorTypeTestPost_0**
> TestConnectionResponse testConnectionApiV1ConnectorsConnectorTypeTestPost_0(testConnectionRequest)

Test a connection configuration.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration,
    TestConnectionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectorType: string; // (default to undefined)
let testConnectionRequest: TestConnectionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.testConnectionApiV1ConnectorsConnectorTypeTestPost_0(
    connectorType,
    testConnectionRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **testConnectionRequest** | **TestConnectionRequest**|  | |
| **connectorType** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TestConnectionResponse**

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

# **uploadConnectionFileApiV1ConnectorsConnectionIdFilesUploadPost**
> FileUploadResponse uploadConnectionFileApiV1ConnectorsConnectionIdFilesUploadPost()

Upload a file to a cloud storage connection.  Accepts a multipart file upload and stores it at the given *path* within the connected cloud storage provider.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let file: File; // (default to undefined)
let path: string; // (optional) (default to '/')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.uploadConnectionFileApiV1ConnectorsConnectionIdFilesUploadPost(
    connectionId,
    file,
    path,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **file** | [**File**] |  | defaults to undefined|
| **path** | [**string**] |  | (optional) defaults to '/'|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**FileUploadResponse**

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

# **uploadConnectionFileApiV1ConnectorsConnectionIdFilesUploadPost_0**
> FileUploadResponse uploadConnectionFileApiV1ConnectorsConnectionIdFilesUploadPost_0()

Upload a file to a cloud storage connection.  Accepts a multipart file upload and stores it at the given *path* within the connected cloud storage provider.

### Example

```typescript
import {
    ConnectorsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectorsApi(configuration);

let connectionId: string; // (default to undefined)
let file: File; // (default to undefined)
let path: string; // (optional) (default to '/')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.uploadConnectionFileApiV1ConnectorsConnectionIdFilesUploadPost_0(
    connectionId,
    file,
    path,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **file** | [**File**] |  | defaults to undefined|
| **path** | [**string**] |  | (optional) defaults to '/'|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**FileUploadResponse**

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

