# SearchApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**booleanSearchApiV1SearchSearchBooleanPost**](#booleansearchapiv1searchsearchbooleanpost) | **POST** /api/v1/search/search/boolean | Boolean Search|
|[**deleteSavedSearchApiV1SearchSavedSearchesSearchIdDelete**](#deletesavedsearchapiv1searchsavedsearchessearchiddelete) | **DELETE** /api/v1/search/saved-searches/{search_id} | Delete Saved Search|
|[**findSimilarDocumentsApiV1SearchDocumentsDocumentIdSimilarGet**](#findsimilardocumentsapiv1searchdocumentsdocumentidsimilarget) | **GET** /api/v1/search/documents/{document_id}/similar | Find Similar Documents|
|[**getSavedSearchApiV1SearchSavedSearchesSearchIdGet**](#getsavedsearchapiv1searchsavedsearchessearchidget) | **GET** /api/v1/search/saved-searches/{search_id} | Get Saved Search|
|[**getSearchAnalyticsApiV1SearchAnalyticsGet**](#getsearchanalyticsapiv1searchanalyticsget) | **GET** /api/v1/search/analytics | Get Search Analytics|
|[**getSearchTypesApiV1SearchTypesGet**](#getsearchtypesapiv1searchtypesget) | **GET** /api/v1/search/types | Get Search Types|
|[**indexDocumentApiV1SearchIndexPost**](#indexdocumentapiv1searchindexpost) | **POST** /api/v1/search/index | Index Document|
|[**listSavedSearchesApiV1SearchSavedSearchesGet**](#listsavedsearchesapiv1searchsavedsearchesget) | **GET** /api/v1/search/saved-searches | List Saved Searches|
|[**regexSearchApiV1SearchSearchRegexPost**](#regexsearchapiv1searchsearchregexpost) | **POST** /api/v1/search/search/regex | Regex Search|
|[**reindexAllApiV1SearchIndexReindexPost**](#reindexallapiv1searchindexreindexpost) | **POST** /api/v1/search/index/reindex | Reindex All|
|[**removeFromIndexApiV1SearchIndexDocumentIdDelete**](#removefromindexapiv1searchindexdocumentiddelete) | **DELETE** /api/v1/search/index/{document_id} | Remove From Index|
|[**runSavedSearchApiV1SearchSavedSearchesSearchIdRunPost**](#runsavedsearchapiv1searchsavedsearchessearchidrunpost) | **POST** /api/v1/search/saved-searches/{search_id}/run | Run Saved Search|
|[**saveSearchApiV1SearchSavedSearchesPost**](#savesearchapiv1searchsavedsearchespost) | **POST** /api/v1/search/saved-searches | Save Search|
|[**searchAndReplaceApiV1SearchSearchReplacePost**](#searchandreplaceapiv1searchsearchreplacepost) | **POST** /api/v1/search/search/replace | Search And Replace|
|[**searchApiV1SearchSearchPost**](#searchapiv1searchsearchpost) | **POST** /api/v1/search/search | Search|
|[**semanticSearchApiV1SearchSearchSemanticPost**](#semanticsearchapiv1searchsearchsemanticpost) | **POST** /api/v1/search/search/semantic | Semantic Search|

# **booleanSearchApiV1SearchSearchBooleanPost**
> any booleanSearchApiV1SearchSearchBooleanPost(backendAppApiRoutesSearchSearchRequest)

Perform boolean search with AND, OR, NOT operators.  Returns:     SearchResponse with boolean match results

### Example

```typescript
import {
    SearchApi,
    Configuration,
    BackendAppApiRoutesSearchSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let backendAppApiRoutesSearchSearchRequest: BackendAppApiRoutesSearchSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.booleanSearchApiV1SearchSearchBooleanPost(
    backendAppApiRoutesSearchSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesSearchSearchRequest** | **BackendAppApiRoutesSearchSearchRequest**|  | |
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

# **deleteSavedSearchApiV1SearchSavedSearchesSearchIdDelete**
> any deleteSavedSearchApiV1SearchSavedSearchesSearchIdDelete()

Delete a saved search.

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let searchId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSavedSearchApiV1SearchSavedSearchesSearchIdDelete(
    searchId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **searchId** | [**string**] |  | defaults to undefined|
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

# **findSimilarDocumentsApiV1SearchDocumentsDocumentIdSimilarGet**
> any findSimilarDocumentsApiV1SearchDocumentsDocumentIdSimilarGet()

Find documents similar to the given document.  Returns:     List of similar documents

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let documentId: string; // (default to undefined)
let limit: number; // (optional) (default to 10)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.findSimilarDocumentsApiV1SearchDocumentsDocumentIdSimilarGet(
    documentId,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 10|
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

# **getSavedSearchApiV1SearchSavedSearchesSearchIdGet**
> any getSavedSearchApiV1SearchSavedSearchesSearchIdGet()

Get a single saved search by ID.  Returns:     SavedSearch configuration

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let searchId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSavedSearchApiV1SearchSavedSearchesSearchIdGet(
    searchId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **searchId** | [**string**] |  | defaults to undefined|
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

# **getSearchAnalyticsApiV1SearchAnalyticsGet**
> any getSearchAnalyticsApiV1SearchAnalyticsGet()

Get search analytics.

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSearchAnalyticsApiV1SearchAnalyticsGet(
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

# **getSearchTypesApiV1SearchTypesGet**
> any getSearchTypesApiV1SearchTypesGet()

Get available search types.  Returns:     List of search types with descriptions

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSearchTypesApiV1SearchTypesGet(
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

# **indexDocumentApiV1SearchIndexPost**
> any indexDocumentApiV1SearchIndexPost(indexDocumentRequest)

Index a document for searching.  Returns:     Success status

### Example

```typescript
import {
    SearchApi,
    Configuration,
    IndexDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let indexDocumentRequest: IndexDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.indexDocumentApiV1SearchIndexPost(
    indexDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **indexDocumentRequest** | **IndexDocumentRequest**|  | |
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

# **listSavedSearchesApiV1SearchSavedSearchesGet**
> any listSavedSearchesApiV1SearchSavedSearchesGet()

List all saved searches.

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSavedSearchesApiV1SearchSavedSearchesGet(
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

# **regexSearchApiV1SearchSearchRegexPost**
> any regexSearchApiV1SearchSearchRegexPost(backendAppApiRoutesSearchSearchRequest)

Perform regex pattern search.  Returns:     SearchResponse with regex matches  Raises:     HTTPException 400: If regex pattern is invalid or potentially dangerous

### Example

```typescript
import {
    SearchApi,
    Configuration,
    BackendAppApiRoutesSearchSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let backendAppApiRoutesSearchSearchRequest: BackendAppApiRoutesSearchSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.regexSearchApiV1SearchSearchRegexPost(
    backendAppApiRoutesSearchSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesSearchSearchRequest** | **BackendAppApiRoutesSearchSearchRequest**|  | |
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

# **reindexAllApiV1SearchIndexReindexPost**
> any reindexAllApiV1SearchIndexReindexPost()

Reindex all documents in the search index.  Returns:     Reindex job status

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.reindexAllApiV1SearchIndexReindexPost(
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

# **removeFromIndexApiV1SearchIndexDocumentIdDelete**
> any removeFromIndexApiV1SearchIndexDocumentIdDelete()

Remove a document from the search index.  Returns:     Success status

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeFromIndexApiV1SearchIndexDocumentIdDelete(
    documentId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
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

# **runSavedSearchApiV1SearchSavedSearchesSearchIdRunPost**
> any runSavedSearchApiV1SearchSavedSearchesSearchIdRunPost()

Run a saved search.

### Example

```typescript
import {
    SearchApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let searchId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runSavedSearchApiV1SearchSavedSearchesSearchIdRunPost(
    searchId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **searchId** | [**string**] |  | defaults to undefined|
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

# **saveSearchApiV1SearchSavedSearchesPost**
> any saveSearchApiV1SearchSavedSearchesPost(saveSearchRequest)

Save a search for later use.  Returns:     SavedSearch configuration

### Example

```typescript
import {
    SearchApi,
    Configuration,
    SaveSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let saveSearchRequest: SaveSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.saveSearchApiV1SearchSavedSearchesPost(
    saveSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **saveSearchRequest** | **SaveSearchRequest**|  | |
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

# **searchAndReplaceApiV1SearchSearchReplacePost**
> any searchAndReplaceApiV1SearchSearchReplacePost(searchReplaceRequest)

Search and replace across documents.  Returns:     Replacement results

### Example

```typescript
import {
    SearchApi,
    Configuration,
    SearchReplaceRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let searchReplaceRequest: SearchReplaceRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.searchAndReplaceApiV1SearchSearchReplacePost(
    searchReplaceRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **searchReplaceRequest** | **SearchReplaceRequest**|  | |
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

# **searchApiV1SearchSearchPost**
> any searchApiV1SearchSearchPost(backendAppApiRoutesSearchSearchRequest)

Perform a search with various options.  Returns:     SearchResponse with results

### Example

```typescript
import {
    SearchApi,
    Configuration,
    BackendAppApiRoutesSearchSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let backendAppApiRoutesSearchSearchRequest: BackendAppApiRoutesSearchSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.searchApiV1SearchSearchPost(
    backendAppApiRoutesSearchSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesSearchSearchRequest** | **BackendAppApiRoutesSearchSearchRequest**|  | |
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

# **semanticSearchApiV1SearchSearchSemanticPost**
> any semanticSearchApiV1SearchSearchSemanticPost(backendAppApiRoutesSearchSearchRequest)

Perform semantic similarity search.  Returns:     SearchResponse with semantically similar results

### Example

```typescript
import {
    SearchApi,
    Configuration,
    BackendAppApiRoutesSearchSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SearchApi(configuration);

let backendAppApiRoutesSearchSearchRequest: BackendAppApiRoutesSearchSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.semanticSearchApiV1SearchSearchSemanticPost(
    backendAppApiRoutesSearchSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesSearchSearchRequest** | **BackendAppApiRoutesSearchSearchRequest**|  | |
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

