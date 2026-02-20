# ConnectionsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**connectionPreviewApiV1ConnectionsConnectionIdPreviewGet**](#connectionpreviewapiv1connectionsconnectionidpreviewget) | **GET** /api/v1/connections/{connection_id}/preview | Connection Preview|
|[**connectionSchemaApiV1ConnectionsConnectionIdSchemaGet**](#connectionschemaapiv1connectionsconnectionidschemaget) | **GET** /api/v1/connections/{connection_id}/schema | Connection Schema|
|[**deleteConnectionApiV1ConnectionsConnectionIdDelete**](#deleteconnectionapiv1connectionsconnectioniddelete) | **DELETE** /api/v1/connections/{connection_id} | Delete Connection|
|[**healthcheckConnectionApiV1ConnectionsConnectionIdHealthPost**](#healthcheckconnectionapiv1connectionsconnectionidhealthpost) | **POST** /api/v1/connections/{connection_id}/health | Healthcheck Connection|
|[**listConnectionsApiV1ConnectionsGet**](#listconnectionsapiv1connectionsget) | **GET** /api/v1/connections | List Connections|
|[**testConnectionApiV1ConnectionsTestPost**](#testconnectionapiv1connectionstestpost) | **POST** /api/v1/connections/test | Test Connection|
|[**upsertConnectionApiV1ConnectionsPost**](#upsertconnectionapiv1connectionspost) | **POST** /api/v1/connections | Upsert Connection|

# **connectionPreviewApiV1ConnectionsConnectionIdPreviewGet**
> any connectionPreviewApiV1ConnectionsConnectionIdPreviewGet()


### Example

```typescript
import {
    ConnectionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectionsApi(configuration);

let connectionId: string; // (default to undefined)
let table: string; // (default to undefined)
let limit: number; // (optional) (default to 10)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.connectionPreviewApiV1ConnectionsConnectionIdPreviewGet(
    connectionId,
    table,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **table** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 10|
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

# **connectionSchemaApiV1ConnectionsConnectionIdSchemaGet**
> any connectionSchemaApiV1ConnectionsConnectionIdSchemaGet()


### Example

```typescript
import {
    ConnectionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectionsApi(configuration);

let connectionId: string; // (default to undefined)
let includeRowCounts: boolean; // (optional) (default to true)
let includeForeignKeys: boolean; // (optional) (default to true)
let sampleRows: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.connectionSchemaApiV1ConnectionsConnectionIdSchemaGet(
    connectionId,
    includeRowCounts,
    includeForeignKeys,
    sampleRows,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | defaults to undefined|
| **includeRowCounts** | [**boolean**] |  | (optional) defaults to true|
| **includeForeignKeys** | [**boolean**] |  | (optional) defaults to true|
| **sampleRows** | [**number**] |  | (optional) defaults to 0|
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

# **deleteConnectionApiV1ConnectionsConnectionIdDelete**
> any deleteConnectionApiV1ConnectionsConnectionIdDelete()


### Example

```typescript
import {
    ConnectionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectionsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteConnectionApiV1ConnectionsConnectionIdDelete(
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

# **healthcheckConnectionApiV1ConnectionsConnectionIdHealthPost**
> any healthcheckConnectionApiV1ConnectionsConnectionIdHealthPost()

Verify a saved connection is still accessible.

### Example

```typescript
import {
    ConnectionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectionsApi(configuration);

let connectionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.healthcheckConnectionApiV1ConnectionsConnectionIdHealthPost(
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

# **listConnectionsApiV1ConnectionsGet**
> any listConnectionsApiV1ConnectionsGet()


### Example

```typescript
import {
    ConnectionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectionsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listConnectionsApiV1ConnectionsGet(
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

# **testConnectionApiV1ConnectionsTestPost**
> any testConnectionApiV1ConnectionsTestPost(connectionTestRequest)


### Example

```typescript
import {
    ConnectionsApi,
    Configuration,
    ConnectionTestRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectionsApi(configuration);

let connectionTestRequest: ConnectionTestRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.testConnectionApiV1ConnectionsTestPost(
    connectionTestRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionTestRequest** | **ConnectionTestRequest**|  | |
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

# **upsertConnectionApiV1ConnectionsPost**
> any upsertConnectionApiV1ConnectionsPost(connectionUpsertRequest)


### Example

```typescript
import {
    ConnectionsApi,
    Configuration,
    ConnectionUpsertRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ConnectionsApi(configuration);

let connectionUpsertRequest: ConnectionUpsertRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.upsertConnectionApiV1ConnectionsPost(
    connectionUpsertRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionUpsertRequest** | **ConnectionUpsertRequest**|  | |
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

