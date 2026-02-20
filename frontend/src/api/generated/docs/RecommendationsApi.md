# RecommendationsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getSimilarTemplatesApiV1RecommendationsTemplatesTemplateIdSimilarGet**](#getsimilartemplatesapiv1recommendationstemplatestemplateidsimilarget) | **GET** /api/v1/recommendations/templates/{template_id}/similar | Get Similar Templates|
|[**getTemplateCatalogApiV1RecommendationsCatalogGet**](#gettemplatecatalogapiv1recommendationscatalogget) | **GET** /api/v1/recommendations/catalog | Get Template Catalog|
|[**recommendTemplatesGetApiV1RecommendationsTemplatesGet**](#recommendtemplatesgetapiv1recommendationstemplatesget) | **GET** /api/v1/recommendations/templates | Recommend Templates Get|
|[**recommendTemplatesPostApiV1RecommendationsTemplatesPost**](#recommendtemplatespostapiv1recommendationstemplatespost) | **POST** /api/v1/recommendations/templates | Recommend Templates Post|

# **getSimilarTemplatesApiV1RecommendationsTemplatesTemplateIdSimilarGet**
> any getSimilarTemplatesApiV1RecommendationsTemplatesTemplateIdSimilarGet()

Get templates similar to a given template.

### Example

```typescript
import {
    RecommendationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RecommendationsApi(configuration);

let templateId: string; // (default to undefined)
let limit: number; // (optional) (default to 3)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSimilarTemplatesApiV1RecommendationsTemplatesTemplateIdSimilarGet(
    templateId,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 3|
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

# **getTemplateCatalogApiV1RecommendationsCatalogGet**
> any getTemplateCatalogApiV1RecommendationsCatalogGet()

Get template catalog for browsing.

### Example

```typescript
import {
    RecommendationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RecommendationsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTemplateCatalogApiV1RecommendationsCatalogGet(
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

# **recommendTemplatesGetApiV1RecommendationsTemplatesGet**
> any recommendTemplatesGetApiV1RecommendationsTemplatesGet()

Get template recommendations based on context (query params).

### Example

```typescript
import {
    RecommendationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RecommendationsApi(configuration);

let connectionId: string; // (optional) (default to undefined)
let context: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 5)
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.recommendTemplatesGetApiV1RecommendationsTemplatesGet(
    connectionId,
    context,
    limit,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|
| **context** | [**string**] |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 5|
| **background** | [**boolean**] |  | (optional) defaults to false|
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

# **recommendTemplatesPostApiV1RecommendationsTemplatesPost**
> any recommendTemplatesPostApiV1RecommendationsTemplatesPost(templateRecommendRequest)

Get template recommendations based on data description and columns.

### Example

```typescript
import {
    RecommendationsApi,
    Configuration,
    TemplateRecommendRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new RecommendationsApi(configuration);

let templateRecommendRequest: TemplateRecommendRequest; //
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.recommendTemplatesPostApiV1RecommendationsTemplatesPost(
    templateRecommendRequest,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateRecommendRequest** | **TemplateRecommendRequest**|  | |
| **background** | [**boolean**] |  | (optional) defaults to false|
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

