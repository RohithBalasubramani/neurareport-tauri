# StateApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**bootstrapStateRouteApiV1StateBootstrapGet**](#bootstrapstaterouteapiv1statebootstrapget) | **GET** /api/v1/state/bootstrap | Bootstrap State Route|
|[**setLastUsedRouteApiV1StateLastUsedPost**](#setlastusedrouteapiv1statelastusedpost) | **POST** /api/v1/state/last-used | Set Last Used Route|

# **bootstrapStateRouteApiV1StateBootstrapGet**
> any bootstrapStateRouteApiV1StateBootstrapGet()

Get bootstrap state for app initialization.  Returns connections, templates, last used selections, and other initialization data needed when the app starts.

### Example

```typescript
import {
    StateApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new StateApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bootstrapStateRouteApiV1StateBootstrapGet(
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

# **setLastUsedRouteApiV1StateLastUsedPost**
> any setLastUsedRouteApiV1StateLastUsedPost(lastUsedPayload)

Record the last-used connection and template IDs for session persistence.

### Example

```typescript
import {
    StateApi,
    Configuration,
    LastUsedPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new StateApi(configuration);

let lastUsedPayload: LastUsedPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.setLastUsedRouteApiV1StateLastUsedPost(
    lastUsedPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **lastUsedPayload** | **LastUsedPayload**|  | |
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

