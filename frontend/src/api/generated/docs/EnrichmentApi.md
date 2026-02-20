# EnrichmentApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**clearCacheApiV1EnrichmentCacheDelete**](#clearcacheapiv1enrichmentcachedelete) | **DELETE** /api/v1/enrichment/cache | Clear Cache|
|[**createSourceApiV1EnrichmentSourcesCreatePost**](#createsourceapiv1enrichmentsourcescreatepost) | **POST** /api/v1/enrichment/sources/create | Create Source|
|[**deleteSourceApiV1EnrichmentSourcesSourceIdDelete**](#deletesourceapiv1enrichmentsourcessourceiddelete) | **DELETE** /api/v1/enrichment/sources/{source_id} | Delete Source|
|[**enrichDataApiV1EnrichmentEnrichPost**](#enrichdataapiv1enrichmentenrichpost) | **POST** /api/v1/enrichment/enrich | Enrich Data|
|[**getCacheStatsApiV1EnrichmentCacheStatsGet**](#getcachestatsapiv1enrichmentcachestatsget) | **GET** /api/v1/enrichment/cache/stats | Get Cache Stats|
|[**getSourceApiV1EnrichmentSourcesSourceIdGet**](#getsourceapiv1enrichmentsourcessourceidget) | **GET** /api/v1/enrichment/sources/{source_id} | Get Source|
|[**listAvailableSourcesApiV1EnrichmentSourcesGet**](#listavailablesourcesapiv1enrichmentsourcesget) | **GET** /api/v1/enrichment/sources | List Available Sources|
|[**listSourceTypesApiV1EnrichmentSourceTypesGet**](#listsourcetypesapiv1enrichmentsourcetypesget) | **GET** /api/v1/enrichment/source-types | List Source Types|
|[**previewEnrichmentApiV1EnrichmentPreviewPost**](#previewenrichmentapiv1enrichmentpreviewpost) | **POST** /api/v1/enrichment/preview | Preview Enrichment|

# **clearCacheApiV1EnrichmentCacheDelete**
> any clearCacheApiV1EnrichmentCacheDelete()

Clear enrichment cache.

### Example

```typescript
import {
    EnrichmentApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let sourceId: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.clearCacheApiV1EnrichmentCacheDelete(
    sourceId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sourceId** | [**string**] |  | (optional) defaults to undefined|
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

# **createSourceApiV1EnrichmentSourcesCreatePost**
> any createSourceApiV1EnrichmentSourcesCreatePost(enrichmentSourceCreate)

Create a custom enrichment source.

### Example

```typescript
import {
    EnrichmentApi,
    Configuration,
    EnrichmentSourceCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let enrichmentSourceCreate: EnrichmentSourceCreate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSourceApiV1EnrichmentSourcesCreatePost(
    enrichmentSourceCreate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **enrichmentSourceCreate** | **EnrichmentSourceCreate**|  | |
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

# **deleteSourceApiV1EnrichmentSourcesSourceIdDelete**
> any deleteSourceApiV1EnrichmentSourcesSourceIdDelete()

Delete a custom enrichment source.

### Example

```typescript
import {
    EnrichmentApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let sourceId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSourceApiV1EnrichmentSourcesSourceIdDelete(
    sourceId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sourceId** | [**string**] |  | defaults to undefined|
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

# **enrichDataApiV1EnrichmentEnrichPost**
> any enrichDataApiV1EnrichmentEnrichPost(simpleEnrichmentRequest)

Enrich data with additional information using selected sources.

### Example

```typescript
import {
    EnrichmentApi,
    Configuration,
    SimpleEnrichmentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let simpleEnrichmentRequest: SimpleEnrichmentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.enrichDataApiV1EnrichmentEnrichPost(
    simpleEnrichmentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **simpleEnrichmentRequest** | **SimpleEnrichmentRequest**|  | |
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

# **getCacheStatsApiV1EnrichmentCacheStatsGet**
> any getCacheStatsApiV1EnrichmentCacheStatsGet()

Get enrichment cache statistics.

### Example

```typescript
import {
    EnrichmentApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCacheStatsApiV1EnrichmentCacheStatsGet(
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

# **getSourceApiV1EnrichmentSourcesSourceIdGet**
> any getSourceApiV1EnrichmentSourcesSourceIdGet()

Get an enrichment source by ID.

### Example

```typescript
import {
    EnrichmentApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let sourceId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSourceApiV1EnrichmentSourcesSourceIdGet(
    sourceId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sourceId** | [**string**] |  | defaults to undefined|
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

# **listAvailableSourcesApiV1EnrichmentSourcesGet**
> any listAvailableSourcesApiV1EnrichmentSourcesGet()

List available enrichment source types.

### Example

```typescript
import {
    EnrichmentApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAvailableSourcesApiV1EnrichmentSourcesGet(
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

# **listSourceTypesApiV1EnrichmentSourceTypesGet**
> any listSourceTypesApiV1EnrichmentSourceTypesGet()

List available enrichment source types (legacy endpoint).

### Example

```typescript
import {
    EnrichmentApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSourceTypesApiV1EnrichmentSourceTypesGet(
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

# **previewEnrichmentApiV1EnrichmentPreviewPost**
> any previewEnrichmentApiV1EnrichmentPreviewPost(simplePreviewRequest)

Preview enrichment results on a sample.

### Example

```typescript
import {
    EnrichmentApi,
    Configuration,
    SimplePreviewRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new EnrichmentApi(configuration);

let simplePreviewRequest: SimplePreviewRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.previewEnrichmentApiV1EnrichmentPreviewPost(
    simplePreviewRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **simplePreviewRequest** | **SimplePreviewRequest**|  | |
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

