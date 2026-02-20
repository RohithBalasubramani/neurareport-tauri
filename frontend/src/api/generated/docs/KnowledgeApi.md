# KnowledgeApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addDocumentApiV1KnowledgeDocumentsPost**](#adddocumentapiv1knowledgedocumentspost) | **POST** /api/v1/knowledge/documents | Add Document|
|[**addDocumentApiV1KnowledgeDocumentsPost_0**](#adddocumentapiv1knowledgedocumentspost_0) | **POST** /api/v1/knowledge/documents | Add Document|
|[**addDocumentToCollectionApiV1KnowledgeCollectionsCollIdDocumentsPost**](#adddocumenttocollectionapiv1knowledgecollectionscolliddocumentspost) | **POST** /api/v1/knowledge/collections/{coll_id}/documents | Add Document To Collection|
|[**addDocumentToCollectionApiV1KnowledgeCollectionsCollIdDocumentsPost_0**](#adddocumenttocollectionapiv1knowledgecollectionscolliddocumentspost_0) | **POST** /api/v1/knowledge/collections/{coll_id}/documents | Add Document To Collection|
|[**addTagToDocumentApiV1KnowledgeDocumentsDocIdTagsPost**](#addtagtodocumentapiv1knowledgedocumentsdocidtagspost) | **POST** /api/v1/knowledge/documents/{doc_id}/tags | Add Tag To Document|
|[**addTagToDocumentApiV1KnowledgeDocumentsDocIdTagsPost_0**](#addtagtodocumentapiv1knowledgedocumentsdocidtagspost_0) | **POST** /api/v1/knowledge/documents/{doc_id}/tags | Add Tag To Document|
|[**autoTagDocumentApiV1KnowledgeAutoTagPost**](#autotagdocumentapiv1knowledgeautotagpost) | **POST** /api/v1/knowledge/auto-tag | Auto Tag Document|
|[**autoTagDocumentApiV1KnowledgeAutoTagPost_0**](#autotagdocumentapiv1knowledgeautotagpost_0) | **POST** /api/v1/knowledge/auto-tag | Auto Tag Document|
|[**buildKnowledgeGraphApiV1KnowledgeKnowledgeGraphPost**](#buildknowledgegraphapiv1knowledgeknowledgegraphpost) | **POST** /api/v1/knowledge/knowledge-graph | Build Knowledge Graph|
|[**buildKnowledgeGraphApiV1KnowledgeKnowledgeGraphPost_0**](#buildknowledgegraphapiv1knowledgeknowledgegraphpost_0) | **POST** /api/v1/knowledge/knowledge-graph | Build Knowledge Graph|
|[**createCollectionApiV1KnowledgeCollectionsPost**](#createcollectionapiv1knowledgecollectionspost) | **POST** /api/v1/knowledge/collections | Create Collection|
|[**createCollectionApiV1KnowledgeCollectionsPost_0**](#createcollectionapiv1knowledgecollectionspost_0) | **POST** /api/v1/knowledge/collections | Create Collection|
|[**createTagApiV1KnowledgeTagsPost**](#createtagapiv1knowledgetagspost) | **POST** /api/v1/knowledge/tags | Create Tag|
|[**createTagApiV1KnowledgeTagsPost_0**](#createtagapiv1knowledgetagspost_0) | **POST** /api/v1/knowledge/tags | Create Tag|
|[**deleteCollectionApiV1KnowledgeCollectionsCollIdDelete**](#deletecollectionapiv1knowledgecollectionscolliddelete) | **DELETE** /api/v1/knowledge/collections/{coll_id} | Delete Collection|
|[**deleteCollectionApiV1KnowledgeCollectionsCollIdDelete_0**](#deletecollectionapiv1knowledgecollectionscolliddelete_0) | **DELETE** /api/v1/knowledge/collections/{coll_id} | Delete Collection|
|[**deleteDocumentApiV1KnowledgeDocumentsDocIdDelete**](#deletedocumentapiv1knowledgedocumentsdociddelete) | **DELETE** /api/v1/knowledge/documents/{doc_id} | Delete Document|
|[**deleteDocumentApiV1KnowledgeDocumentsDocIdDelete_0**](#deletedocumentapiv1knowledgedocumentsdociddelete_0) | **DELETE** /api/v1/knowledge/documents/{doc_id} | Delete Document|
|[**deleteTagApiV1KnowledgeTagsTagIdDelete**](#deletetagapiv1knowledgetagstagiddelete) | **DELETE** /api/v1/knowledge/tags/{tag_id} | Delete Tag|
|[**deleteTagApiV1KnowledgeTagsTagIdDelete_0**](#deletetagapiv1knowledgetagstagiddelete_0) | **DELETE** /api/v1/knowledge/tags/{tag_id} | Delete Tag|
|[**findRelatedDocumentsApiV1KnowledgeRelatedPost**](#findrelateddocumentsapiv1knowledgerelatedpost) | **POST** /api/v1/knowledge/related | Find Related Documents|
|[**findRelatedDocumentsApiV1KnowledgeRelatedPost_0**](#findrelateddocumentsapiv1knowledgerelatedpost_0) | **POST** /api/v1/knowledge/related | Find Related Documents|
|[**generateFaqApiV1KnowledgeFaqPost**](#generatefaqapiv1knowledgefaqpost) | **POST** /api/v1/knowledge/faq | Generate Faq|
|[**generateFaqApiV1KnowledgeFaqPost_0**](#generatefaqapiv1knowledgefaqpost_0) | **POST** /api/v1/knowledge/faq | Generate Faq|
|[**getCollectionApiV1KnowledgeCollectionsCollIdGet**](#getcollectionapiv1knowledgecollectionscollidget) | **GET** /api/v1/knowledge/collections/{coll_id} | Get Collection|
|[**getCollectionApiV1KnowledgeCollectionsCollIdGet_0**](#getcollectionapiv1knowledgecollectionscollidget_0) | **GET** /api/v1/knowledge/collections/{coll_id} | Get Collection|
|[**getDocumentActivityApiV1KnowledgeDocumentsDocIdActivityGet**](#getdocumentactivityapiv1knowledgedocumentsdocidactivityget) | **GET** /api/v1/knowledge/documents/{doc_id}/activity | Get Document Activity|
|[**getDocumentActivityApiV1KnowledgeDocumentsDocIdActivityGet_0**](#getdocumentactivityapiv1knowledgedocumentsdocidactivityget_0) | **GET** /api/v1/knowledge/documents/{doc_id}/activity | Get Document Activity|
|[**getDocumentApiV1KnowledgeDocumentsDocIdGet**](#getdocumentapiv1knowledgedocumentsdocidget) | **GET** /api/v1/knowledge/documents/{doc_id} | Get Document|
|[**getDocumentApiV1KnowledgeDocumentsDocIdGet_0**](#getdocumentapiv1knowledgedocumentsdocidget_0) | **GET** /api/v1/knowledge/documents/{doc_id} | Get Document|
|[**getLibraryStatsApiV1KnowledgeStatsGet**](#getlibrarystatsapiv1knowledgestatsget) | **GET** /api/v1/knowledge/stats | Get Library Stats|
|[**getLibraryStatsApiV1KnowledgeStatsGet_0**](#getlibrarystatsapiv1knowledgestatsget_0) | **GET** /api/v1/knowledge/stats | Get Library Stats|
|[**listCollectionsApiV1KnowledgeCollectionsGet**](#listcollectionsapiv1knowledgecollectionsget) | **GET** /api/v1/knowledge/collections | List Collections|
|[**listCollectionsApiV1KnowledgeCollectionsGet_0**](#listcollectionsapiv1knowledgecollectionsget_0) | **GET** /api/v1/knowledge/collections | List Collections|
|[**listDocumentsApiV1KnowledgeDocumentsGet**](#listdocumentsapiv1knowledgedocumentsget) | **GET** /api/v1/knowledge/documents | List Documents|
|[**listDocumentsApiV1KnowledgeDocumentsGet_0**](#listdocumentsapiv1knowledgedocumentsget_0) | **GET** /api/v1/knowledge/documents | List Documents|
|[**listTagsApiV1KnowledgeTagsGet**](#listtagsapiv1knowledgetagsget) | **GET** /api/v1/knowledge/tags | List Tags|
|[**listTagsApiV1KnowledgeTagsGet_0**](#listtagsapiv1knowledgetagsget_0) | **GET** /api/v1/knowledge/tags | List Tags|
|[**removeDocumentFromCollectionApiV1KnowledgeCollectionsCollIdDocumentsDocIdDelete**](#removedocumentfromcollectionapiv1knowledgecollectionscolliddocumentsdociddelete) | **DELETE** /api/v1/knowledge/collections/{coll_id}/documents/{doc_id} | Remove Document From Collection|
|[**removeDocumentFromCollectionApiV1KnowledgeCollectionsCollIdDocumentsDocIdDelete_0**](#removedocumentfromcollectionapiv1knowledgecollectionscolliddocumentsdociddelete_0) | **DELETE** /api/v1/knowledge/collections/{coll_id}/documents/{doc_id} | Remove Document From Collection|
|[**removeTagFromDocumentApiV1KnowledgeDocumentsDocIdTagsTagIdDelete**](#removetagfromdocumentapiv1knowledgedocumentsdocidtagstagiddelete) | **DELETE** /api/v1/knowledge/documents/{doc_id}/tags/{tag_id} | Remove Tag From Document|
|[**removeTagFromDocumentApiV1KnowledgeDocumentsDocIdTagsTagIdDelete_0**](#removetagfromdocumentapiv1knowledgedocumentsdocidtagstagiddelete_0) | **DELETE** /api/v1/knowledge/documents/{doc_id}/tags/{tag_id} | Remove Tag From Document|
|[**searchDocumentsApiV1KnowledgeSearchPost**](#searchdocumentsapiv1knowledgesearchpost) | **POST** /api/v1/knowledge/search | Search Documents|
|[**searchDocumentsApiV1KnowledgeSearchPost_0**](#searchdocumentsapiv1knowledgesearchpost_0) | **POST** /api/v1/knowledge/search | Search Documents|
|[**searchDocumentsGetApiV1KnowledgeSearchGet**](#searchdocumentsgetapiv1knowledgesearchget) | **GET** /api/v1/knowledge/search | Search Documents Get|
|[**searchDocumentsGetApiV1KnowledgeSearchGet_0**](#searchdocumentsgetapiv1knowledgesearchget_0) | **GET** /api/v1/knowledge/search | Search Documents Get|
|[**semanticSearchApiV1KnowledgeSearchSemanticPost**](#semanticsearchapiv1knowledgesearchsemanticpost) | **POST** /api/v1/knowledge/search/semantic | Semantic Search|
|[**semanticSearchApiV1KnowledgeSearchSemanticPost_0**](#semanticsearchapiv1knowledgesearchsemanticpost_0) | **POST** /api/v1/knowledge/search/semantic | Semantic Search|
|[**toggleFavoriteApiV1KnowledgeDocumentsDocIdFavoritePost**](#togglefavoriteapiv1knowledgedocumentsdocidfavoritepost) | **POST** /api/v1/knowledge/documents/{doc_id}/favorite | Toggle Favorite|
|[**toggleFavoriteApiV1KnowledgeDocumentsDocIdFavoritePost_0**](#togglefavoriteapiv1knowledgedocumentsdocidfavoritepost_0) | **POST** /api/v1/knowledge/documents/{doc_id}/favorite | Toggle Favorite|
|[**updateCollectionApiV1KnowledgeCollectionsCollIdPut**](#updatecollectionapiv1knowledgecollectionscollidput) | **PUT** /api/v1/knowledge/collections/{coll_id} | Update Collection|
|[**updateCollectionApiV1KnowledgeCollectionsCollIdPut_0**](#updatecollectionapiv1knowledgecollectionscollidput_0) | **PUT** /api/v1/knowledge/collections/{coll_id} | Update Collection|
|[**updateDocumentApiV1KnowledgeDocumentsDocIdPut**](#updatedocumentapiv1knowledgedocumentsdocidput) | **PUT** /api/v1/knowledge/documents/{doc_id} | Update Document|
|[**updateDocumentApiV1KnowledgeDocumentsDocIdPut_0**](#updatedocumentapiv1knowledgedocumentsdocidput_0) | **PUT** /api/v1/knowledge/documents/{doc_id} | Update Document|

# **addDocumentApiV1KnowledgeDocumentsPost**
> LibraryDocumentResponse addDocumentApiV1KnowledgeDocumentsPost(libraryDocumentCreate)

Add a document to the library.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    LibraryDocumentCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let libraryDocumentCreate: LibraryDocumentCreate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDocumentApiV1KnowledgeDocumentsPost(
    libraryDocumentCreate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **libraryDocumentCreate** | **LibraryDocumentCreate**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LibraryDocumentResponse**

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

# **addDocumentApiV1KnowledgeDocumentsPost_0**
> LibraryDocumentResponse addDocumentApiV1KnowledgeDocumentsPost_0(libraryDocumentCreate)

Add a document to the library.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    LibraryDocumentCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let libraryDocumentCreate: LibraryDocumentCreate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDocumentApiV1KnowledgeDocumentsPost_0(
    libraryDocumentCreate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **libraryDocumentCreate** | **LibraryDocumentCreate**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LibraryDocumentResponse**

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

# **addDocumentToCollectionApiV1KnowledgeCollectionsCollIdDocumentsPost**
> any addDocumentToCollectionApiV1KnowledgeCollectionsCollIdDocumentsPost(collectionAddDocumentRequest)

Add a document to a collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    CollectionAddDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let collectionAddDocumentRequest: CollectionAddDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDocumentToCollectionApiV1KnowledgeCollectionsCollIdDocumentsPost(
    collId,
    collectionAddDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collectionAddDocumentRequest** | **CollectionAddDocumentRequest**|  | |
| **collId** | [**string**] |  | defaults to undefined|
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

# **addDocumentToCollectionApiV1KnowledgeCollectionsCollIdDocumentsPost_0**
> any addDocumentToCollectionApiV1KnowledgeCollectionsCollIdDocumentsPost_0(collectionAddDocumentRequest)

Add a document to a collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    CollectionAddDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let collectionAddDocumentRequest: CollectionAddDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDocumentToCollectionApiV1KnowledgeCollectionsCollIdDocumentsPost_0(
    collId,
    collectionAddDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collectionAddDocumentRequest** | **CollectionAddDocumentRequest**|  | |
| **collId** | [**string**] |  | defaults to undefined|
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

# **addTagToDocumentApiV1KnowledgeDocumentsDocIdTagsPost**
> any addTagToDocumentApiV1KnowledgeDocumentsDocIdTagsPost(documentAddTagRequest)

Add a tag to a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    DocumentAddTagRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let documentAddTagRequest: DocumentAddTagRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addTagToDocumentApiV1KnowledgeDocumentsDocIdTagsPost(
    docId,
    documentAddTagRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentAddTagRequest** | **DocumentAddTagRequest**|  | |
| **docId** | [**string**] |  | defaults to undefined|
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

# **addTagToDocumentApiV1KnowledgeDocumentsDocIdTagsPost_0**
> any addTagToDocumentApiV1KnowledgeDocumentsDocIdTagsPost_0(documentAddTagRequest)

Add a tag to a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    DocumentAddTagRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let documentAddTagRequest: DocumentAddTagRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addTagToDocumentApiV1KnowledgeDocumentsDocIdTagsPost_0(
    docId,
    documentAddTagRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentAddTagRequest** | **DocumentAddTagRequest**|  | |
| **docId** | [**string**] |  | defaults to undefined|
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

# **autoTagDocumentApiV1KnowledgeAutoTagPost**
> any autoTagDocumentApiV1KnowledgeAutoTagPost(autoTagRequest)

Auto-suggest tags for a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    AutoTagRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let autoTagRequest: AutoTagRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.autoTagDocumentApiV1KnowledgeAutoTagPost(
    autoTagRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **autoTagRequest** | **AutoTagRequest**|  | |
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

# **autoTagDocumentApiV1KnowledgeAutoTagPost_0**
> any autoTagDocumentApiV1KnowledgeAutoTagPost_0(autoTagRequest)

Auto-suggest tags for a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    AutoTagRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let autoTagRequest: AutoTagRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.autoTagDocumentApiV1KnowledgeAutoTagPost_0(
    autoTagRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **autoTagRequest** | **AutoTagRequest**|  | |
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

# **buildKnowledgeGraphApiV1KnowledgeKnowledgeGraphPost**
> KnowledgeGraphResponse buildKnowledgeGraphApiV1KnowledgeKnowledgeGraphPost(knowledgeGraphRequest)

Build a knowledge graph from documents.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    KnowledgeGraphRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let knowledgeGraphRequest: KnowledgeGraphRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.buildKnowledgeGraphApiV1KnowledgeKnowledgeGraphPost(
    knowledgeGraphRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **knowledgeGraphRequest** | **KnowledgeGraphRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**KnowledgeGraphResponse**

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

# **buildKnowledgeGraphApiV1KnowledgeKnowledgeGraphPost_0**
> KnowledgeGraphResponse buildKnowledgeGraphApiV1KnowledgeKnowledgeGraphPost_0(knowledgeGraphRequest)

Build a knowledge graph from documents.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    KnowledgeGraphRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let knowledgeGraphRequest: KnowledgeGraphRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.buildKnowledgeGraphApiV1KnowledgeKnowledgeGraphPost_0(
    knowledgeGraphRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **knowledgeGraphRequest** | **KnowledgeGraphRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**KnowledgeGraphResponse**

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

# **createCollectionApiV1KnowledgeCollectionsPost**
> CollectionResponse createCollectionApiV1KnowledgeCollectionsPost(collectionCreate)

Create a new collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    CollectionCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collectionCreate: CollectionCreate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCollectionApiV1KnowledgeCollectionsPost(
    collectionCreate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collectionCreate** | **CollectionCreate**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CollectionResponse**

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

# **createCollectionApiV1KnowledgeCollectionsPost_0**
> CollectionResponse createCollectionApiV1KnowledgeCollectionsPost_0(collectionCreate)

Create a new collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    CollectionCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collectionCreate: CollectionCreate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCollectionApiV1KnowledgeCollectionsPost_0(
    collectionCreate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collectionCreate** | **CollectionCreate**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CollectionResponse**

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

# **createTagApiV1KnowledgeTagsPost**
> TagResponse createTagApiV1KnowledgeTagsPost(tagCreate)

Create a new tag.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    TagCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let tagCreate: TagCreate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTagApiV1KnowledgeTagsPost(
    tagCreate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tagCreate** | **TagCreate**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TagResponse**

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

# **createTagApiV1KnowledgeTagsPost_0**
> TagResponse createTagApiV1KnowledgeTagsPost_0(tagCreate)

Create a new tag.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    TagCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let tagCreate: TagCreate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTagApiV1KnowledgeTagsPost_0(
    tagCreate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tagCreate** | **TagCreate**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TagResponse**

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

# **deleteCollectionApiV1KnowledgeCollectionsCollIdDelete**
> any deleteCollectionApiV1KnowledgeCollectionsCollIdDelete()

Delete a collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteCollectionApiV1KnowledgeCollectionsCollIdDelete(
    collId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collId** | [**string**] |  | defaults to undefined|
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

# **deleteCollectionApiV1KnowledgeCollectionsCollIdDelete_0**
> any deleteCollectionApiV1KnowledgeCollectionsCollIdDelete_0()

Delete a collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteCollectionApiV1KnowledgeCollectionsCollIdDelete_0(
    collId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collId** | [**string**] |  | defaults to undefined|
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

# **deleteDocumentApiV1KnowledgeDocumentsDocIdDelete**
> any deleteDocumentApiV1KnowledgeDocumentsDocIdDelete()

Delete a document from the library.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteDocumentApiV1KnowledgeDocumentsDocIdDelete(
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
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

# **deleteDocumentApiV1KnowledgeDocumentsDocIdDelete_0**
> any deleteDocumentApiV1KnowledgeDocumentsDocIdDelete_0()

Delete a document from the library.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteDocumentApiV1KnowledgeDocumentsDocIdDelete_0(
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
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

# **deleteTagApiV1KnowledgeTagsTagIdDelete**
> any deleteTagApiV1KnowledgeTagsTagIdDelete()

Delete a tag.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let tagId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTagApiV1KnowledgeTagsTagIdDelete(
    tagId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tagId** | [**string**] |  | defaults to undefined|
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

# **deleteTagApiV1KnowledgeTagsTagIdDelete_0**
> any deleteTagApiV1KnowledgeTagsTagIdDelete_0()

Delete a tag.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let tagId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTagApiV1KnowledgeTagsTagIdDelete_0(
    tagId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tagId** | [**string**] |  | defaults to undefined|
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

# **findRelatedDocumentsApiV1KnowledgeRelatedPost**
> RelatedDocumentsResponse findRelatedDocumentsApiV1KnowledgeRelatedPost(relatedDocumentsRequest)

Find documents related to a given document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    RelatedDocumentsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let relatedDocumentsRequest: RelatedDocumentsRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.findRelatedDocumentsApiV1KnowledgeRelatedPost(
    relatedDocumentsRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **relatedDocumentsRequest** | **RelatedDocumentsRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**RelatedDocumentsResponse**

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

# **findRelatedDocumentsApiV1KnowledgeRelatedPost_0**
> RelatedDocumentsResponse findRelatedDocumentsApiV1KnowledgeRelatedPost_0(relatedDocumentsRequest)

Find documents related to a given document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    RelatedDocumentsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let relatedDocumentsRequest: RelatedDocumentsRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.findRelatedDocumentsApiV1KnowledgeRelatedPost_0(
    relatedDocumentsRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **relatedDocumentsRequest** | **RelatedDocumentsRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**RelatedDocumentsResponse**

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

# **generateFaqApiV1KnowledgeFaqPost**
> any generateFaqApiV1KnowledgeFaqPost(fAQGenerateRequest)

Generate FAQ from documents.  By default runs as a background job so the UI can track progress. Pass ?background=false for synchronous response.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    FAQGenerateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let fAQGenerateRequest: FAQGenerateRequest; //
let background: boolean; // (optional) (default to true)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateFaqApiV1KnowledgeFaqPost(
    fAQGenerateRequest,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **fAQGenerateRequest** | **FAQGenerateRequest**|  | |
| **background** | [**boolean**] |  | (optional) defaults to true|
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

# **generateFaqApiV1KnowledgeFaqPost_0**
> any generateFaqApiV1KnowledgeFaqPost_0(fAQGenerateRequest)

Generate FAQ from documents.  By default runs as a background job so the UI can track progress. Pass ?background=false for synchronous response.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    FAQGenerateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let fAQGenerateRequest: FAQGenerateRequest; //
let background: boolean; // (optional) (default to true)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateFaqApiV1KnowledgeFaqPost_0(
    fAQGenerateRequest,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **fAQGenerateRequest** | **FAQGenerateRequest**|  | |
| **background** | [**boolean**] |  | (optional) defaults to true|
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

# **getCollectionApiV1KnowledgeCollectionsCollIdGet**
> CollectionResponse getCollectionApiV1KnowledgeCollectionsCollIdGet()

Get a collection by ID.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCollectionApiV1KnowledgeCollectionsCollIdGet(
    collId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CollectionResponse**

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

# **getCollectionApiV1KnowledgeCollectionsCollIdGet_0**
> CollectionResponse getCollectionApiV1KnowledgeCollectionsCollIdGet_0()

Get a collection by ID.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCollectionApiV1KnowledgeCollectionsCollIdGet_0(
    collId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CollectionResponse**

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

# **getDocumentActivityApiV1KnowledgeDocumentsDocIdActivityGet**
> any getDocumentActivityApiV1KnowledgeDocumentsDocIdActivityGet()

Get the activity log for a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentActivityApiV1KnowledgeDocumentsDocIdActivityGet(
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
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

# **getDocumentActivityApiV1KnowledgeDocumentsDocIdActivityGet_0**
> any getDocumentActivityApiV1KnowledgeDocumentsDocIdActivityGet_0()

Get the activity log for a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentActivityApiV1KnowledgeDocumentsDocIdActivityGet_0(
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
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

# **getDocumentApiV1KnowledgeDocumentsDocIdGet**
> LibraryDocumentResponse getDocumentApiV1KnowledgeDocumentsDocIdGet()

Get a document by ID.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentApiV1KnowledgeDocumentsDocIdGet(
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LibraryDocumentResponse**

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

# **getDocumentApiV1KnowledgeDocumentsDocIdGet_0**
> LibraryDocumentResponse getDocumentApiV1KnowledgeDocumentsDocIdGet_0()

Get a document by ID.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentApiV1KnowledgeDocumentsDocIdGet_0(
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LibraryDocumentResponse**

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

# **getLibraryStatsApiV1KnowledgeStatsGet**
> any getLibraryStatsApiV1KnowledgeStatsGet()

Get library statistics including total documents, collections, tags, and storage usage.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getLibraryStatsApiV1KnowledgeStatsGet(
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

# **getLibraryStatsApiV1KnowledgeStatsGet_0**
> any getLibraryStatsApiV1KnowledgeStatsGet_0()

Get library statistics including total documents, collections, tags, and storage usage.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getLibraryStatsApiV1KnowledgeStatsGet_0(
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

# **listCollectionsApiV1KnowledgeCollectionsGet**
> Array<CollectionResponse> listCollectionsApiV1KnowledgeCollectionsGet()

List all collections.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCollectionsApiV1KnowledgeCollectionsGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CollectionResponse>**

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

# **listCollectionsApiV1KnowledgeCollectionsGet_0**
> Array<CollectionResponse> listCollectionsApiV1KnowledgeCollectionsGet_0()

List all collections.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCollectionsApiV1KnowledgeCollectionsGet_0(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CollectionResponse>**

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

# **listDocumentsApiV1KnowledgeDocumentsGet**
> Array<LibraryDocumentResponse> listDocumentsApiV1KnowledgeDocumentsGet()

List documents with optional filtering.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collectionId: string; // (optional) (default to undefined)
let tags: string; //Comma-separated tag names (optional) (default to undefined)
let documentType: BackendAppSchemasKnowledgeLibraryDocumentType; // (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDocumentsApiV1KnowledgeDocumentsGet(
    collectionId,
    tags,
    documentType,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collectionId** | [**string**] |  | (optional) defaults to undefined|
| **tags** | [**string**] | Comma-separated tag names | (optional) defaults to undefined|
| **documentType** | **BackendAppSchemasKnowledgeLibraryDocumentType** |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<LibraryDocumentResponse>**

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

# **listDocumentsApiV1KnowledgeDocumentsGet_0**
> Array<LibraryDocumentResponse> listDocumentsApiV1KnowledgeDocumentsGet_0()

List documents with optional filtering.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collectionId: string; // (optional) (default to undefined)
let tags: string; //Comma-separated tag names (optional) (default to undefined)
let documentType: BackendAppSchemasKnowledgeLibraryDocumentType; // (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDocumentsApiV1KnowledgeDocumentsGet_0(
    collectionId,
    tags,
    documentType,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collectionId** | [**string**] |  | (optional) defaults to undefined|
| **tags** | [**string**] | Comma-separated tag names | (optional) defaults to undefined|
| **documentType** | **BackendAppSchemasKnowledgeLibraryDocumentType** |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<LibraryDocumentResponse>**

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

# **listTagsApiV1KnowledgeTagsGet**
> Array<TagResponse> listTagsApiV1KnowledgeTagsGet()

List all tags.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTagsApiV1KnowledgeTagsGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TagResponse>**

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

# **listTagsApiV1KnowledgeTagsGet_0**
> Array<TagResponse> listTagsApiV1KnowledgeTagsGet_0()

List all tags.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTagsApiV1KnowledgeTagsGet_0(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TagResponse>**

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

# **removeDocumentFromCollectionApiV1KnowledgeCollectionsCollIdDocumentsDocIdDelete**
> any removeDocumentFromCollectionApiV1KnowledgeCollectionsCollIdDocumentsDocIdDelete()

Remove a document from a collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeDocumentFromCollectionApiV1KnowledgeCollectionsCollIdDocumentsDocIdDelete(
    collId,
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collId** | [**string**] |  | defaults to undefined|
| **docId** | [**string**] |  | defaults to undefined|
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

# **removeDocumentFromCollectionApiV1KnowledgeCollectionsCollIdDocumentsDocIdDelete_0**
> any removeDocumentFromCollectionApiV1KnowledgeCollectionsCollIdDocumentsDocIdDelete_0()

Remove a document from a collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeDocumentFromCollectionApiV1KnowledgeCollectionsCollIdDocumentsDocIdDelete_0(
    collId,
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collId** | [**string**] |  | defaults to undefined|
| **docId** | [**string**] |  | defaults to undefined|
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

# **removeTagFromDocumentApiV1KnowledgeDocumentsDocIdTagsTagIdDelete**
> any removeTagFromDocumentApiV1KnowledgeDocumentsDocIdTagsTagIdDelete()

Remove a tag from a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let tagId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeTagFromDocumentApiV1KnowledgeDocumentsDocIdTagsTagIdDelete(
    docId,
    tagId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
| **tagId** | [**string**] |  | defaults to undefined|
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

# **removeTagFromDocumentApiV1KnowledgeDocumentsDocIdTagsTagIdDelete_0**
> any removeTagFromDocumentApiV1KnowledgeDocumentsDocIdTagsTagIdDelete_0()

Remove a tag from a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let tagId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeTagFromDocumentApiV1KnowledgeDocumentsDocIdTagsTagIdDelete_0(
    docId,
    tagId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
| **tagId** | [**string**] |  | defaults to undefined|
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

# **searchDocumentsApiV1KnowledgeSearchPost**
> SearchResponse searchDocumentsApiV1KnowledgeSearchPost(backendAppSchemasKnowledgeLibrarySearchRequest)

Full-text search across documents.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    BackendAppSchemasKnowledgeLibrarySearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let backendAppSchemasKnowledgeLibrarySearchRequest: BackendAppSchemasKnowledgeLibrarySearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.searchDocumentsApiV1KnowledgeSearchPost(
    backendAppSchemasKnowledgeLibrarySearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasKnowledgeLibrarySearchRequest** | **BackendAppSchemasKnowledgeLibrarySearchRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SearchResponse**

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

# **searchDocumentsApiV1KnowledgeSearchPost_0**
> SearchResponse searchDocumentsApiV1KnowledgeSearchPost_0(backendAppSchemasKnowledgeLibrarySearchRequest)

Full-text search across documents.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    BackendAppSchemasKnowledgeLibrarySearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let backendAppSchemasKnowledgeLibrarySearchRequest: BackendAppSchemasKnowledgeLibrarySearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.searchDocumentsApiV1KnowledgeSearchPost_0(
    backendAppSchemasKnowledgeLibrarySearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasKnowledgeLibrarySearchRequest** | **BackendAppSchemasKnowledgeLibrarySearchRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SearchResponse**

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

# **searchDocumentsGetApiV1KnowledgeSearchGet**
> any searchDocumentsGetApiV1KnowledgeSearchGet()

Full-text search (GET endpoint).

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let query: string; // (default to undefined)
let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.searchDocumentsGetApiV1KnowledgeSearchGet(
    query,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **query** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
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

# **searchDocumentsGetApiV1KnowledgeSearchGet_0**
> any searchDocumentsGetApiV1KnowledgeSearchGet_0()

Full-text search (GET endpoint).

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let query: string; // (default to undefined)
let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.searchDocumentsGetApiV1KnowledgeSearchGet_0(
    query,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **query** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
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

# **semanticSearchApiV1KnowledgeSearchSemanticPost**
> SearchResponse semanticSearchApiV1KnowledgeSearchSemanticPost(backendAppSchemasKnowledgeLibrarySemanticSearchRequest)

Semantic search using embeddings.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    BackendAppSchemasKnowledgeLibrarySemanticSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let backendAppSchemasKnowledgeLibrarySemanticSearchRequest: BackendAppSchemasKnowledgeLibrarySemanticSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.semanticSearchApiV1KnowledgeSearchSemanticPost(
    backendAppSchemasKnowledgeLibrarySemanticSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasKnowledgeLibrarySemanticSearchRequest** | **BackendAppSchemasKnowledgeLibrarySemanticSearchRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SearchResponse**

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

# **semanticSearchApiV1KnowledgeSearchSemanticPost_0**
> SearchResponse semanticSearchApiV1KnowledgeSearchSemanticPost_0(backendAppSchemasKnowledgeLibrarySemanticSearchRequest)

Semantic search using embeddings.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    BackendAppSchemasKnowledgeLibrarySemanticSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let backendAppSchemasKnowledgeLibrarySemanticSearchRequest: BackendAppSchemasKnowledgeLibrarySemanticSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.semanticSearchApiV1KnowledgeSearchSemanticPost_0(
    backendAppSchemasKnowledgeLibrarySemanticSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasKnowledgeLibrarySemanticSearchRequest** | **BackendAppSchemasKnowledgeLibrarySemanticSearchRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SearchResponse**

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

# **toggleFavoriteApiV1KnowledgeDocumentsDocIdFavoritePost**
> any toggleFavoriteApiV1KnowledgeDocumentsDocIdFavoritePost()

Toggle favorite status for a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.toggleFavoriteApiV1KnowledgeDocumentsDocIdFavoritePost(
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
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

# **toggleFavoriteApiV1KnowledgeDocumentsDocIdFavoritePost_0**
> any toggleFavoriteApiV1KnowledgeDocumentsDocIdFavoritePost_0()

Toggle favorite status for a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.toggleFavoriteApiV1KnowledgeDocumentsDocIdFavoritePost_0(
    docId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **docId** | [**string**] |  | defaults to undefined|
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

# **updateCollectionApiV1KnowledgeCollectionsCollIdPut**
> CollectionResponse updateCollectionApiV1KnowledgeCollectionsCollIdPut(collectionUpdate)

Update a collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    CollectionUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let collectionUpdate: CollectionUpdate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCollectionApiV1KnowledgeCollectionsCollIdPut(
    collId,
    collectionUpdate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collectionUpdate** | **CollectionUpdate**|  | |
| **collId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CollectionResponse**

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

# **updateCollectionApiV1KnowledgeCollectionsCollIdPut_0**
> CollectionResponse updateCollectionApiV1KnowledgeCollectionsCollIdPut_0(collectionUpdate)

Update a collection.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    CollectionUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let collId: string; // (default to undefined)
let collectionUpdate: CollectionUpdate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCollectionApiV1KnowledgeCollectionsCollIdPut_0(
    collId,
    collectionUpdate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **collectionUpdate** | **CollectionUpdate**|  | |
| **collId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CollectionResponse**

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

# **updateDocumentApiV1KnowledgeDocumentsDocIdPut**
> LibraryDocumentResponse updateDocumentApiV1KnowledgeDocumentsDocIdPut(libraryDocumentUpdate)

Update a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    LibraryDocumentUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let libraryDocumentUpdate: LibraryDocumentUpdate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateDocumentApiV1KnowledgeDocumentsDocIdPut(
    docId,
    libraryDocumentUpdate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **libraryDocumentUpdate** | **LibraryDocumentUpdate**|  | |
| **docId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LibraryDocumentResponse**

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

# **updateDocumentApiV1KnowledgeDocumentsDocIdPut_0**
> LibraryDocumentResponse updateDocumentApiV1KnowledgeDocumentsDocIdPut_0(libraryDocumentUpdate)

Update a document.

### Example

```typescript
import {
    KnowledgeApi,
    Configuration,
    LibraryDocumentUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new KnowledgeApi(configuration);

let docId: string; // (default to undefined)
let libraryDocumentUpdate: LibraryDocumentUpdate; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateDocumentApiV1KnowledgeDocumentsDocIdPut_0(
    docId,
    libraryDocumentUpdate,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **libraryDocumentUpdate** | **LibraryDocumentUpdate**|  | |
| **docId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LibraryDocumentResponse**

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

