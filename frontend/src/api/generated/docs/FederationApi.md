# FederationApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createVirtualSchemaApiV1FederationSchemasPost**](#createvirtualschemaapiv1federationschemaspost) | **POST** /api/v1/federation/schemas | Create Virtual Schema|
|[**deleteVirtualSchemaApiV1FederationSchemasSchemaIdDelete**](#deletevirtualschemaapiv1federationschemasschemaiddelete) | **DELETE** /api/v1/federation/schemas/{schema_id} | Delete Virtual Schema|
|[**executeFederatedQueryApiV1FederationQueryPost**](#executefederatedqueryapiv1federationquerypost) | **POST** /api/v1/federation/query | Execute Federated Query|
|[**getVirtualSchemaApiV1FederationSchemasSchemaIdGet**](#getvirtualschemaapiv1federationschemasschemaidget) | **GET** /api/v1/federation/schemas/{schema_id} | Get Virtual Schema|
|[**listVirtualSchemasApiV1FederationSchemasGet**](#listvirtualschemasapiv1federationschemasget) | **GET** /api/v1/federation/schemas | List Virtual Schemas|
|[**suggestJoinsApiV1FederationSuggestJoinsPost**](#suggestjoinsapiv1federationsuggestjoinspost) | **POST** /api/v1/federation/suggest-joins | Suggest Joins|

# **createVirtualSchemaApiV1FederationSchemasPost**
> any createVirtualSchemaApiV1FederationSchemasPost(virtualSchemaCreate)

Create a virtual schema spanning multiple databases.

### Example

```typescript
import {
    FederationApi,
    Configuration,
    VirtualSchemaCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new FederationApi(configuration);

let virtualSchemaCreate: VirtualSchemaCreate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createVirtualSchemaApiV1FederationSchemasPost(
    virtualSchemaCreate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **virtualSchemaCreate** | **VirtualSchemaCreate**|  | |
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

# **deleteVirtualSchemaApiV1FederationSchemasSchemaIdDelete**
> any deleteVirtualSchemaApiV1FederationSchemasSchemaIdDelete()

Delete a virtual schema.

### Example

```typescript
import {
    FederationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new FederationApi(configuration);

let schemaId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteVirtualSchemaApiV1FederationSchemasSchemaIdDelete(
    schemaId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **schemaId** | [**string**] |  | defaults to undefined|
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

# **executeFederatedQueryApiV1FederationQueryPost**
> any executeFederatedQueryApiV1FederationQueryPost(federatedQueryRequest)

Execute a federated query across multiple databases.

### Example

```typescript
import {
    FederationApi,
    Configuration,
    FederatedQueryRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new FederationApi(configuration);

let federatedQueryRequest: FederatedQueryRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.executeFederatedQueryApiV1FederationQueryPost(
    federatedQueryRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **federatedQueryRequest** | **FederatedQueryRequest**|  | |
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

# **getVirtualSchemaApiV1FederationSchemasSchemaIdGet**
> any getVirtualSchemaApiV1FederationSchemasSchemaIdGet()

Get a virtual schema by ID.

### Example

```typescript
import {
    FederationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new FederationApi(configuration);

let schemaId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getVirtualSchemaApiV1FederationSchemasSchemaIdGet(
    schemaId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **schemaId** | [**string**] |  | defaults to undefined|
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

# **listVirtualSchemasApiV1FederationSchemasGet**
> any listVirtualSchemasApiV1FederationSchemasGet()

List all virtual schemas.

### Example

```typescript
import {
    FederationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new FederationApi(configuration);

let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listVirtualSchemasApiV1FederationSchemasGet(
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

# **suggestJoinsApiV1FederationSuggestJoinsPost**
> any suggestJoinsApiV1FederationSuggestJoinsPost(suggestJoinsRequest)

Get AI-suggested joins between tables in different connections.

### Example

```typescript
import {
    FederationApi,
    Configuration,
    SuggestJoinsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new FederationApi(configuration);

let suggestJoinsRequest: SuggestJoinsRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestJoinsApiV1FederationSuggestJoinsPost(
    suggestJoinsRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestJoinsRequest** | **SuggestJoinsRequest**|  | |
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

