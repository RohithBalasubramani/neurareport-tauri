# DocumentsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addCommentApiV1DocumentsDocumentIdCommentsPost**](#addcommentapiv1documentsdocumentidcommentspost) | **POST** /api/v1/documents/{document_id}/comments | Add Comment|
|[**addCommentApiV1DocumentsDocumentIdCommentsPost_0**](#addcommentapiv1documentsdocumentidcommentspost_0) | **POST** /api/v1/documents/{document_id}/comments | Add Comment|
|[**addWatermarkApiV1DocumentsDocumentIdPdfWatermarkPost**](#addwatermarkapiv1documentsdocumentidpdfwatermarkpost) | **POST** /api/v1/documents/{document_id}/pdf/watermark | Add Watermark|
|[**addWatermarkApiV1DocumentsDocumentIdPdfWatermarkPost_0**](#addwatermarkapiv1documentsdocumentidpdfwatermarkpost_0) | **POST** /api/v1/documents/{document_id}/pdf/watermark | Add Watermark|
|[**adjustToneApiV1DocumentsDocumentIdAiTonePost**](#adjusttoneapiv1documentsdocumentidaitonepost) | **POST** /api/v1/documents/{document_id}/ai/tone | Adjust Tone|
|[**adjustToneApiV1DocumentsDocumentIdAiTonePost_0**](#adjusttoneapiv1documentsdocumentidaitonepost_0) | **POST** /api/v1/documents/{document_id}/ai/tone | Adjust Tone|
|[**checkGrammarApiV1DocumentsDocumentIdAiGrammarPost**](#checkgrammarapiv1documentsdocumentidaigrammarpost) | **POST** /api/v1/documents/{document_id}/ai/grammar | Check Grammar|
|[**checkGrammarApiV1DocumentsDocumentIdAiGrammarPost_0**](#checkgrammarapiv1documentsdocumentidaigrammarpost_0) | **POST** /api/v1/documents/{document_id}/ai/grammar | Check Grammar|
|[**createDocumentApiV1DocumentsPost**](#createdocumentapiv1documentspost) | **POST** /api/v1/documents | Create Document|
|[**createDocumentApiV1DocumentsPost_0**](#createdocumentapiv1documentspost_0) | **POST** /api/v1/documents | Create Document|
|[**createFromTemplateApiV1DocumentsTemplatesTemplateIdCreatePost**](#createfromtemplateapiv1documentstemplatestemplateidcreatepost) | **POST** /api/v1/documents/templates/{template_id}/create | Create From Template|
|[**createFromTemplateApiV1DocumentsTemplatesTemplateIdCreatePost_0**](#createfromtemplateapiv1documentstemplatestemplateidcreatepost_0) | **POST** /api/v1/documents/templates/{template_id}/create | Create From Template|
|[**deleteCommentApiV1DocumentsDocumentIdCommentsCommentIdDelete**](#deletecommentapiv1documentsdocumentidcommentscommentiddelete) | **DELETE** /api/v1/documents/{document_id}/comments/{comment_id} | Delete Comment|
|[**deleteCommentApiV1DocumentsDocumentIdCommentsCommentIdDelete_0**](#deletecommentapiv1documentsdocumentidcommentscommentiddelete_0) | **DELETE** /api/v1/documents/{document_id}/comments/{comment_id} | Delete Comment|
|[**deleteDocumentApiV1DocumentsDocumentIdDelete**](#deletedocumentapiv1documentsdocumentiddelete) | **DELETE** /api/v1/documents/{document_id} | Delete Document|
|[**deleteDocumentApiV1DocumentsDocumentIdDelete_0**](#deletedocumentapiv1documentsdocumentiddelete_0) | **DELETE** /api/v1/documents/{document_id} | Delete Document|
|[**expandTextApiV1DocumentsDocumentIdAiExpandPost**](#expandtextapiv1documentsdocumentidaiexpandpost) | **POST** /api/v1/documents/{document_id}/ai/expand | Expand Text|
|[**expandTextApiV1DocumentsDocumentIdAiExpandPost_0**](#expandtextapiv1documentsdocumentidaiexpandpost_0) | **POST** /api/v1/documents/{document_id}/ai/expand | Expand Text|
|[**exportDocumentApiV1DocumentsDocumentIdExportGet**](#exportdocumentapiv1documentsdocumentidexportget) | **GET** /api/v1/documents/{document_id}/export | Export Document|
|[**exportDocumentApiV1DocumentsDocumentIdExportGet_0**](#exportdocumentapiv1documentsdocumentidexportget_0) | **GET** /api/v1/documents/{document_id}/export | Export Document|
|[**getCollaborationPresenceApiV1DocumentsDocumentIdCollaboratePresenceGet**](#getcollaborationpresenceapiv1documentsdocumentidcollaboratepresenceget) | **GET** /api/v1/documents/{document_id}/collaborate/presence | Get Collaboration Presence|
|[**getCollaborationPresenceApiV1DocumentsDocumentIdCollaboratePresenceGet_0**](#getcollaborationpresenceapiv1documentsdocumentidcollaboratepresenceget_0) | **GET** /api/v1/documents/{document_id}/collaborate/presence | Get Collaboration Presence|
|[**getCommentsApiV1DocumentsDocumentIdCommentsGet**](#getcommentsapiv1documentsdocumentidcommentsget) | **GET** /api/v1/documents/{document_id}/comments | Get Comments|
|[**getCommentsApiV1DocumentsDocumentIdCommentsGet_0**](#getcommentsapiv1documentsdocumentidcommentsget_0) | **GET** /api/v1/documents/{document_id}/comments | Get Comments|
|[**getDocumentApiV1DocumentsDocumentIdGet**](#getdocumentapiv1documentsdocumentidget) | **GET** /api/v1/documents/{document_id} | Get Document|
|[**getDocumentApiV1DocumentsDocumentIdGet_0**](#getdocumentapiv1documentsdocumentidget_0) | **GET** /api/v1/documents/{document_id} | Get Document|
|[**getDocumentVersionApiV1DocumentsDocumentIdVersionsVersionGet**](#getdocumentversionapiv1documentsdocumentidversionsversionget) | **GET** /api/v1/documents/{document_id}/versions/{version} | Get Document Version|
|[**getDocumentVersionApiV1DocumentsDocumentIdVersionsVersionGet_0**](#getdocumentversionapiv1documentsdocumentidversionsversionget_0) | **GET** /api/v1/documents/{document_id}/versions/{version} | Get Document Version|
|[**getDocumentVersionsApiV1DocumentsDocumentIdVersionsGet**](#getdocumentversionsapiv1documentsdocumentidversionsget) | **GET** /api/v1/documents/{document_id}/versions | Get Document Versions|
|[**getDocumentVersionsApiV1DocumentsDocumentIdVersionsGet_0**](#getdocumentversionsapiv1documentsdocumentidversionsget_0) | **GET** /api/v1/documents/{document_id}/versions | Get Document Versions|
|[**listDocumentsApiV1DocumentsGet**](#listdocumentsapiv1documentsget) | **GET** /api/v1/documents | List Documents|
|[**listDocumentsApiV1DocumentsGet_0**](#listdocumentsapiv1documentsget_0) | **GET** /api/v1/documents | List Documents|
|[**listTemplatesApiV1DocumentsTemplatesGet**](#listtemplatesapiv1documentstemplatesget) | **GET** /api/v1/documents/templates | List Templates|
|[**listTemplatesApiV1DocumentsTemplatesGet_0**](#listtemplatesapiv1documentstemplatesget_0) | **GET** /api/v1/documents/templates | List Templates|
|[**mergePdfsApiV1DocumentsMergePost**](#mergepdfsapiv1documentsmergepost) | **POST** /api/v1/documents/merge | Merge Pdfs|
|[**mergePdfsApiV1DocumentsMergePost_0**](#mergepdfsapiv1documentsmergepost_0) | **POST** /api/v1/documents/merge | Merge Pdfs|
|[**redactPdfApiV1DocumentsDocumentIdPdfRedactPost**](#redactpdfapiv1documentsdocumentidpdfredactpost) | **POST** /api/v1/documents/{document_id}/pdf/redact | Redact Pdf|
|[**redactPdfApiV1DocumentsDocumentIdPdfRedactPost_0**](#redactpdfapiv1documentsdocumentidpdfredactpost_0) | **POST** /api/v1/documents/{document_id}/pdf/redact | Redact Pdf|
|[**reorderPdfPagesApiV1DocumentsDocumentIdPdfReorderPost**](#reorderpdfpagesapiv1documentsdocumentidpdfreorderpost) | **POST** /api/v1/documents/{document_id}/pdf/reorder | Reorder Pdf Pages|
|[**reorderPdfPagesApiV1DocumentsDocumentIdPdfReorderPost_0**](#reorderpdfpagesapiv1documentsdocumentidpdfreorderpost_0) | **POST** /api/v1/documents/{document_id}/pdf/reorder | Reorder Pdf Pages|
|[**replyToCommentApiV1DocumentsDocumentIdCommentsCommentIdReplyPost**](#replytocommentapiv1documentsdocumentidcommentscommentidreplypost) | **POST** /api/v1/documents/{document_id}/comments/{comment_id}/reply | Reply To Comment|
|[**replyToCommentApiV1DocumentsDocumentIdCommentsCommentIdReplyPost_0**](#replytocommentapiv1documentsdocumentidcommentscommentidreplypost_0) | **POST** /api/v1/documents/{document_id}/comments/{comment_id}/reply | Reply To Comment|
|[**resolveCommentApiV1DocumentsDocumentIdCommentsCommentIdResolvePatch**](#resolvecommentapiv1documentsdocumentidcommentscommentidresolvepatch) | **PATCH** /api/v1/documents/{document_id}/comments/{comment_id}/resolve | Resolve Comment|
|[**resolveCommentApiV1DocumentsDocumentIdCommentsCommentIdResolvePatch_0**](#resolvecommentapiv1documentsdocumentidcommentscommentidresolvepatch_0) | **PATCH** /api/v1/documents/{document_id}/comments/{comment_id}/resolve | Resolve Comment|
|[**restoreDocumentVersionApiV1DocumentsDocumentIdVersionsVersionRestorePost**](#restoredocumentversionapiv1documentsdocumentidversionsversionrestorepost) | **POST** /api/v1/documents/{document_id}/versions/{version}/restore | Restore Document Version|
|[**restoreDocumentVersionApiV1DocumentsDocumentIdVersionsVersionRestorePost_0**](#restoredocumentversionapiv1documentsdocumentidversionsversionrestorepost_0) | **POST** /api/v1/documents/{document_id}/versions/{version}/restore | Restore Document Version|
|[**rewriteTextApiV1DocumentsDocumentIdAiRewritePost**](#rewritetextapiv1documentsdocumentidairewritepost) | **POST** /api/v1/documents/{document_id}/ai/rewrite | Rewrite Text|
|[**rewriteTextApiV1DocumentsDocumentIdAiRewritePost_0**](#rewritetextapiv1documentsdocumentidairewritepost_0) | **POST** /api/v1/documents/{document_id}/ai/rewrite | Rewrite Text|
|[**rotatePdfPagesApiV1DocumentsDocumentIdPdfRotatePost**](#rotatepdfpagesapiv1documentsdocumentidpdfrotatepost) | **POST** /api/v1/documents/{document_id}/pdf/rotate | Rotate Pdf Pages|
|[**rotatePdfPagesApiV1DocumentsDocumentIdPdfRotatePost_0**](#rotatepdfpagesapiv1documentsdocumentidpdfrotatepost_0) | **POST** /api/v1/documents/{document_id}/pdf/rotate | Rotate Pdf Pages|
|[**saveAsTemplateApiV1DocumentsDocumentIdSaveAsTemplatePost**](#saveastemplateapiv1documentsdocumentidsaveastemplatepost) | **POST** /api/v1/documents/{document_id}/save-as-template | Save As Template|
|[**saveAsTemplateApiV1DocumentsDocumentIdSaveAsTemplatePost_0**](#saveastemplateapiv1documentsdocumentidsaveastemplatepost_0) | **POST** /api/v1/documents/{document_id}/save-as-template | Save As Template|
|[**splitPdfApiV1DocumentsDocumentIdPdfSplitPost**](#splitpdfapiv1documentsdocumentidpdfsplitpost) | **POST** /api/v1/documents/{document_id}/pdf/split | Split Pdf|
|[**splitPdfApiV1DocumentsDocumentIdPdfSplitPost_0**](#splitpdfapiv1documentsdocumentidpdfsplitpost_0) | **POST** /api/v1/documents/{document_id}/pdf/split | Split Pdf|
|[**startCollaborationApiV1DocumentsDocumentIdCollaboratePost**](#startcollaborationapiv1documentsdocumentidcollaboratepost) | **POST** /api/v1/documents/{document_id}/collaborate | Start Collaboration|
|[**startCollaborationApiV1DocumentsDocumentIdCollaboratePost_0**](#startcollaborationapiv1documentsdocumentidcollaboratepost_0) | **POST** /api/v1/documents/{document_id}/collaborate | Start Collaboration|
|[**summarizeTextApiV1DocumentsDocumentIdAiSummarizePost**](#summarizetextapiv1documentsdocumentidaisummarizepost) | **POST** /api/v1/documents/{document_id}/ai/summarize | Summarize Text|
|[**summarizeTextApiV1DocumentsDocumentIdAiSummarizePost_0**](#summarizetextapiv1documentsdocumentidaisummarizepost_0) | **POST** /api/v1/documents/{document_id}/ai/summarize | Summarize Text|
|[**translateTextApiV1DocumentsDocumentIdAiTranslatePost**](#translatetextapiv1documentsdocumentidaitranslatepost) | **POST** /api/v1/documents/{document_id}/ai/translate | Translate Text|
|[**translateTextApiV1DocumentsDocumentIdAiTranslatePost_0**](#translatetextapiv1documentsdocumentidaitranslatepost_0) | **POST** /api/v1/documents/{document_id}/ai/translate | Translate Text|
|[**updateDocumentApiV1DocumentsDocumentIdPut**](#updatedocumentapiv1documentsdocumentidput) | **PUT** /api/v1/documents/{document_id} | Update Document|
|[**updateDocumentApiV1DocumentsDocumentIdPut_0**](#updatedocumentapiv1documentsdocumentidput_0) | **PUT** /api/v1/documents/{document_id} | Update Document|
|[**updateUserPresenceApiV1DocumentsDocumentIdPresencePut**](#updateuserpresenceapiv1documentsdocumentidpresenceput) | **PUT** /api/v1/documents/{document_id}/presence | Update User Presence|
|[**updateUserPresenceApiV1DocumentsDocumentIdPresencePut_0**](#updateuserpresenceapiv1documentsdocumentidpresenceput_0) | **PUT** /api/v1/documents/{document_id}/presence | Update User Presence|

# **addCommentApiV1DocumentsDocumentIdCommentsPost**
> CommentResponse addCommentApiV1DocumentsDocumentIdCommentsPost(backendAppSchemasDocumentsDocumentCommentRequest)

Add a comment to a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    BackendAppSchemasDocumentsDocumentCommentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let backendAppSchemasDocumentsDocumentCommentRequest: BackendAppSchemasDocumentsDocumentCommentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addCommentApiV1DocumentsDocumentIdCommentsPost(
    documentId,
    backendAppSchemasDocumentsDocumentCommentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasDocumentsDocumentCommentRequest** | **BackendAppSchemasDocumentsDocumentCommentRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CommentResponse**

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

# **addCommentApiV1DocumentsDocumentIdCommentsPost_0**
> CommentResponse addCommentApiV1DocumentsDocumentIdCommentsPost_0(backendAppSchemasDocumentsDocumentCommentRequest)

Add a comment to a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    BackendAppSchemasDocumentsDocumentCommentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let backendAppSchemasDocumentsDocumentCommentRequest: BackendAppSchemasDocumentsDocumentCommentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addCommentApiV1DocumentsDocumentIdCommentsPost_0(
    documentId,
    backendAppSchemasDocumentsDocumentCommentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasDocumentsDocumentCommentRequest** | **BackendAppSchemasDocumentsDocumentCommentRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CommentResponse**

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

# **addWatermarkApiV1DocumentsDocumentIdPdfWatermarkPost**
> any addWatermarkApiV1DocumentsDocumentIdPdfWatermarkPost(pDFWatermarkRequest)

Add watermark to a PDF document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFWatermarkRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFWatermarkRequest: PDFWatermarkRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addWatermarkApiV1DocumentsDocumentIdPdfWatermarkPost(
    documentId,
    pDFWatermarkRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFWatermarkRequest** | **PDFWatermarkRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **addWatermarkApiV1DocumentsDocumentIdPdfWatermarkPost_0**
> any addWatermarkApiV1DocumentsDocumentIdPdfWatermarkPost_0(pDFWatermarkRequest)

Add watermark to a PDF document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFWatermarkRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFWatermarkRequest: PDFWatermarkRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addWatermarkApiV1DocumentsDocumentIdPdfWatermarkPost_0(
    documentId,
    pDFWatermarkRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFWatermarkRequest** | **PDFWatermarkRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **adjustToneApiV1DocumentsDocumentIdAiTonePost**
> AIWritingResponse adjustToneApiV1DocumentsDocumentIdAiTonePost(aIWritingRequest)

Adjust the tone of text content.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.adjustToneApiV1DocumentsDocumentIdAiTonePost(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **adjustToneApiV1DocumentsDocumentIdAiTonePost_0**
> AIWritingResponse adjustToneApiV1DocumentsDocumentIdAiTonePost_0(aIWritingRequest)

Adjust the tone of text content.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.adjustToneApiV1DocumentsDocumentIdAiTonePost_0(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **checkGrammarApiV1DocumentsDocumentIdAiGrammarPost**
> AIWritingResponse checkGrammarApiV1DocumentsDocumentIdAiGrammarPost(aIWritingRequest)

Check grammar and spelling in text.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkGrammarApiV1DocumentsDocumentIdAiGrammarPost(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **checkGrammarApiV1DocumentsDocumentIdAiGrammarPost_0**
> AIWritingResponse checkGrammarApiV1DocumentsDocumentIdAiGrammarPost_0(aIWritingRequest)

Check grammar and spelling in text.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkGrammarApiV1DocumentsDocumentIdAiGrammarPost_0(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **createDocumentApiV1DocumentsPost**
> DocumentResponse createDocumentApiV1DocumentsPost(createDocumentRequest)

Create a new document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    CreateDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let createDocumentRequest: CreateDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createDocumentApiV1DocumentsPost(
    createDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createDocumentRequest** | **CreateDocumentRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentResponse**

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

# **createDocumentApiV1DocumentsPost_0**
> DocumentResponse createDocumentApiV1DocumentsPost_0(createDocumentRequest)

Create a new document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    CreateDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let createDocumentRequest: CreateDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createDocumentApiV1DocumentsPost_0(
    createDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createDocumentRequest** | **CreateDocumentRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentResponse**

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

# **createFromTemplateApiV1DocumentsTemplatesTemplateIdCreatePost**
> DocumentResponse createFromTemplateApiV1DocumentsTemplatesTemplateIdCreatePost(backendAppSchemasDocumentsDocumentCreateFromTemplateRequest)

Create a new document from a template.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    BackendAppSchemasDocumentsDocumentCreateFromTemplateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let templateId: string; // (default to undefined)
let backendAppSchemasDocumentsDocumentCreateFromTemplateRequest: BackendAppSchemasDocumentsDocumentCreateFromTemplateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createFromTemplateApiV1DocumentsTemplatesTemplateIdCreatePost(
    templateId,
    backendAppSchemasDocumentsDocumentCreateFromTemplateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasDocumentsDocumentCreateFromTemplateRequest** | **BackendAppSchemasDocumentsDocumentCreateFromTemplateRequest**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentResponse**

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

# **createFromTemplateApiV1DocumentsTemplatesTemplateIdCreatePost_0**
> DocumentResponse createFromTemplateApiV1DocumentsTemplatesTemplateIdCreatePost_0(backendAppSchemasDocumentsDocumentCreateFromTemplateRequest)

Create a new document from a template.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    BackendAppSchemasDocumentsDocumentCreateFromTemplateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let templateId: string; // (default to undefined)
let backendAppSchemasDocumentsDocumentCreateFromTemplateRequest: BackendAppSchemasDocumentsDocumentCreateFromTemplateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createFromTemplateApiV1DocumentsTemplatesTemplateIdCreatePost_0(
    templateId,
    backendAppSchemasDocumentsDocumentCreateFromTemplateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasDocumentsDocumentCreateFromTemplateRequest** | **BackendAppSchemasDocumentsDocumentCreateFromTemplateRequest**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentResponse**

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

# **deleteCommentApiV1DocumentsDocumentIdCommentsCommentIdDelete**
> any deleteCommentApiV1DocumentsDocumentIdCommentsCommentIdDelete()

Delete a comment from a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let commentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteCommentApiV1DocumentsDocumentIdCommentsCommentIdDelete(
    documentId,
    commentId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **commentId** | [**string**] |  | defaults to undefined|
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

# **deleteCommentApiV1DocumentsDocumentIdCommentsCommentIdDelete_0**
> any deleteCommentApiV1DocumentsDocumentIdCommentsCommentIdDelete_0()

Delete a comment from a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let commentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteCommentApiV1DocumentsDocumentIdCommentsCommentIdDelete_0(
    documentId,
    commentId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **commentId** | [**string**] |  | defaults to undefined|
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

# **deleteDocumentApiV1DocumentsDocumentIdDelete**
> any deleteDocumentApiV1DocumentsDocumentIdDelete()

Delete a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteDocumentApiV1DocumentsDocumentIdDelete(
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

# **deleteDocumentApiV1DocumentsDocumentIdDelete_0**
> any deleteDocumentApiV1DocumentsDocumentIdDelete_0()

Delete a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteDocumentApiV1DocumentsDocumentIdDelete_0(
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

# **expandTextApiV1DocumentsDocumentIdAiExpandPost**
> AIWritingResponse expandTextApiV1DocumentsDocumentIdAiExpandPost(aIWritingRequest)

Expand bullet points or short text into paragraphs.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.expandTextApiV1DocumentsDocumentIdAiExpandPost(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **expandTextApiV1DocumentsDocumentIdAiExpandPost_0**
> AIWritingResponse expandTextApiV1DocumentsDocumentIdAiExpandPost_0(aIWritingRequest)

Expand bullet points or short text into paragraphs.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.expandTextApiV1DocumentsDocumentIdAiExpandPost_0(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **exportDocumentApiV1DocumentsDocumentIdExportGet**
> any exportDocumentApiV1DocumentsDocumentIdExportGet()

Export a document in the specified format.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let format: string; //Export format: pdf, docx, html, md (optional) (default to 'html')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportDocumentApiV1DocumentsDocumentIdExportGet(
    documentId,
    format,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **format** | [**string**] | Export format: pdf, docx, html, md | (optional) defaults to 'html'|
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

# **exportDocumentApiV1DocumentsDocumentIdExportGet_0**
> any exportDocumentApiV1DocumentsDocumentIdExportGet_0()

Export a document in the specified format.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let format: string; //Export format: pdf, docx, html, md (optional) (default to 'html')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportDocumentApiV1DocumentsDocumentIdExportGet_0(
    documentId,
    format,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **format** | [**string**] | Export format: pdf, docx, html, md | (optional) defaults to 'html'|
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

# **getCollaborationPresenceApiV1DocumentsDocumentIdCollaboratePresenceGet**
> any getCollaborationPresenceApiV1DocumentsDocumentIdCollaboratePresenceGet()

Get current collaborators for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCollaborationPresenceApiV1DocumentsDocumentIdCollaboratePresenceGet(
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

# **getCollaborationPresenceApiV1DocumentsDocumentIdCollaboratePresenceGet_0**
> any getCollaborationPresenceApiV1DocumentsDocumentIdCollaboratePresenceGet_0()

Get current collaborators for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCollaborationPresenceApiV1DocumentsDocumentIdCollaboratePresenceGet_0(
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

# **getCommentsApiV1DocumentsDocumentIdCommentsGet**
> any getCommentsApiV1DocumentsDocumentIdCommentsGet()

Get all comments for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCommentsApiV1DocumentsDocumentIdCommentsGet(
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

# **getCommentsApiV1DocumentsDocumentIdCommentsGet_0**
> any getCommentsApiV1DocumentsDocumentIdCommentsGet_0()

Get all comments for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCommentsApiV1DocumentsDocumentIdCommentsGet_0(
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

# **getDocumentApiV1DocumentsDocumentIdGet**
> DocumentResponse getDocumentApiV1DocumentsDocumentIdGet()

Get a document by ID.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentApiV1DocumentsDocumentIdGet(
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

**DocumentResponse**

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

# **getDocumentApiV1DocumentsDocumentIdGet_0**
> DocumentResponse getDocumentApiV1DocumentsDocumentIdGet_0()

Get a document by ID.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentApiV1DocumentsDocumentIdGet_0(
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

**DocumentResponse**

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

# **getDocumentVersionApiV1DocumentsDocumentIdVersionsVersionGet**
> any getDocumentVersionApiV1DocumentsDocumentIdVersionsVersionGet()

Get a specific version of a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let version: number; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentVersionApiV1DocumentsDocumentIdVersionsVersionGet(
    documentId,
    version,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **version** | [**number**] |  | defaults to undefined|
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

# **getDocumentVersionApiV1DocumentsDocumentIdVersionsVersionGet_0**
> any getDocumentVersionApiV1DocumentsDocumentIdVersionsVersionGet_0()

Get a specific version of a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let version: number; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentVersionApiV1DocumentsDocumentIdVersionsVersionGet_0(
    documentId,
    version,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **version** | [**number**] |  | defaults to undefined|
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

# **getDocumentVersionsApiV1DocumentsDocumentIdVersionsGet**
> any getDocumentVersionsApiV1DocumentsDocumentIdVersionsGet()

Get version history for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentVersionsApiV1DocumentsDocumentIdVersionsGet(
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

# **getDocumentVersionsApiV1DocumentsDocumentIdVersionsGet_0**
> any getDocumentVersionsApiV1DocumentsDocumentIdVersionsGet_0()

Get version history for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDocumentVersionsApiV1DocumentsDocumentIdVersionsGet_0(
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

# **listDocumentsApiV1DocumentsGet**
> DocumentListResponse listDocumentsApiV1DocumentsGet()

List documents with optional filters.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let isTemplate: boolean; // (optional) (default to undefined)
let tags: string; //Comma-separated tags (optional) (default to undefined)
let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDocumentsApiV1DocumentsGet(
    isTemplate,
    tags,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **isTemplate** | [**boolean**] |  | (optional) defaults to undefined|
| **tags** | [**string**] | Comma-separated tags | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentListResponse**

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

# **listDocumentsApiV1DocumentsGet_0**
> DocumentListResponse listDocumentsApiV1DocumentsGet_0()

List documents with optional filters.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let isTemplate: boolean; // (optional) (default to undefined)
let tags: string; //Comma-separated tags (optional) (default to undefined)
let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDocumentsApiV1DocumentsGet_0(
    isTemplate,
    tags,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **isTemplate** | [**boolean**] |  | (optional) defaults to undefined|
| **tags** | [**string**] | Comma-separated tags | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentListResponse**

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

# **listTemplatesApiV1DocumentsTemplatesGet**
> DocumentListResponse listTemplatesApiV1DocumentsTemplatesGet()

List document templates.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let tags: string; //Comma-separated tags (optional) (default to undefined)
let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTemplatesApiV1DocumentsTemplatesGet(
    tags,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tags** | [**string**] | Comma-separated tags | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentListResponse**

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

# **listTemplatesApiV1DocumentsTemplatesGet_0**
> DocumentListResponse listTemplatesApiV1DocumentsTemplatesGet_0()

List document templates.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let tags: string; //Comma-separated tags (optional) (default to undefined)
let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTemplatesApiV1DocumentsTemplatesGet_0(
    tags,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tags** | [**string**] | Comma-separated tags | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentListResponse**

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

# **mergePdfsApiV1DocumentsMergePost**
> any mergePdfsApiV1DocumentsMergePost(pDFMergeRequest)

Merge multiple PDF documents into one.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFMergeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let pDFMergeRequest: PDFMergeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mergePdfsApiV1DocumentsMergePost(
    pDFMergeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFMergeRequest** | **PDFMergeRequest**|  | |
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

# **mergePdfsApiV1DocumentsMergePost_0**
> any mergePdfsApiV1DocumentsMergePost_0(pDFMergeRequest)

Merge multiple PDF documents into one.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFMergeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let pDFMergeRequest: PDFMergeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mergePdfsApiV1DocumentsMergePost_0(
    pDFMergeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFMergeRequest** | **PDFMergeRequest**|  | |
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

# **redactPdfApiV1DocumentsDocumentIdPdfRedactPost**
> any redactPdfApiV1DocumentsDocumentIdPdfRedactPost(pDFRedactRequest)

Redact regions in a PDF document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFRedactRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFRedactRequest: PDFRedactRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.redactPdfApiV1DocumentsDocumentIdPdfRedactPost(
    documentId,
    pDFRedactRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFRedactRequest** | **PDFRedactRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **redactPdfApiV1DocumentsDocumentIdPdfRedactPost_0**
> any redactPdfApiV1DocumentsDocumentIdPdfRedactPost_0(pDFRedactRequest)

Redact regions in a PDF document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFRedactRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFRedactRequest: PDFRedactRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.redactPdfApiV1DocumentsDocumentIdPdfRedactPost_0(
    documentId,
    pDFRedactRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFRedactRequest** | **PDFRedactRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **reorderPdfPagesApiV1DocumentsDocumentIdPdfReorderPost**
> any reorderPdfPagesApiV1DocumentsDocumentIdPdfReorderPost(pDFReorderRequest)

Reorder pages in a PDF document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFReorderRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFReorderRequest: PDFReorderRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.reorderPdfPagesApiV1DocumentsDocumentIdPdfReorderPost(
    documentId,
    pDFReorderRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFReorderRequest** | **PDFReorderRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **reorderPdfPagesApiV1DocumentsDocumentIdPdfReorderPost_0**
> any reorderPdfPagesApiV1DocumentsDocumentIdPdfReorderPost_0(pDFReorderRequest)

Reorder pages in a PDF document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFReorderRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFReorderRequest: PDFReorderRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.reorderPdfPagesApiV1DocumentsDocumentIdPdfReorderPost_0(
    documentId,
    pDFReorderRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFReorderRequest** | **PDFReorderRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **replyToCommentApiV1DocumentsDocumentIdCommentsCommentIdReplyPost**
> CommentResponse replyToCommentApiV1DocumentsDocumentIdCommentsCommentIdReplyPost(commentReplyRequest)

Reply to an existing comment.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    CommentReplyRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let commentId: string; // (default to undefined)
let commentReplyRequest: CommentReplyRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.replyToCommentApiV1DocumentsDocumentIdCommentsCommentIdReplyPost(
    documentId,
    commentId,
    commentReplyRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **commentReplyRequest** | **CommentReplyRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **commentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CommentResponse**

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

# **replyToCommentApiV1DocumentsDocumentIdCommentsCommentIdReplyPost_0**
> CommentResponse replyToCommentApiV1DocumentsDocumentIdCommentsCommentIdReplyPost_0(commentReplyRequest)

Reply to an existing comment.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    CommentReplyRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let commentId: string; // (default to undefined)
let commentReplyRequest: CommentReplyRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.replyToCommentApiV1DocumentsDocumentIdCommentsCommentIdReplyPost_0(
    documentId,
    commentId,
    commentReplyRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **commentReplyRequest** | **CommentReplyRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **commentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CommentResponse**

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

# **resolveCommentApiV1DocumentsDocumentIdCommentsCommentIdResolvePatch**
> any resolveCommentApiV1DocumentsDocumentIdCommentsCommentIdResolvePatch()

Resolve a comment.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let commentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resolveCommentApiV1DocumentsDocumentIdCommentsCommentIdResolvePatch(
    documentId,
    commentId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **commentId** | [**string**] |  | defaults to undefined|
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

# **resolveCommentApiV1DocumentsDocumentIdCommentsCommentIdResolvePatch_0**
> any resolveCommentApiV1DocumentsDocumentIdCommentsCommentIdResolvePatch_0()

Resolve a comment.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let commentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resolveCommentApiV1DocumentsDocumentIdCommentsCommentIdResolvePatch_0(
    documentId,
    commentId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **commentId** | [**string**] |  | defaults to undefined|
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

# **restoreDocumentVersionApiV1DocumentsDocumentIdVersionsVersionRestorePost**
> DocumentResponse restoreDocumentVersionApiV1DocumentsDocumentIdVersionsVersionRestorePost()

Restore a document to a specific version.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let version: number; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.restoreDocumentVersionApiV1DocumentsDocumentIdVersionsVersionRestorePost(
    documentId,
    version,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **version** | [**number**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentResponse**

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

# **restoreDocumentVersionApiV1DocumentsDocumentIdVersionsVersionRestorePost_0**
> DocumentResponse restoreDocumentVersionApiV1DocumentsDocumentIdVersionsVersionRestorePost_0()

Restore a document to a specific version.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let version: number; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.restoreDocumentVersionApiV1DocumentsDocumentIdVersionsVersionRestorePost_0(
    documentId,
    version,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
| **version** | [**number**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentResponse**

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

# **rewriteTextApiV1DocumentsDocumentIdAiRewritePost**
> AIWritingResponse rewriteTextApiV1DocumentsDocumentIdAiRewritePost(aIWritingRequest)

Rewrite text for clarity or different tone.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.rewriteTextApiV1DocumentsDocumentIdAiRewritePost(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **rewriteTextApiV1DocumentsDocumentIdAiRewritePost_0**
> AIWritingResponse rewriteTextApiV1DocumentsDocumentIdAiRewritePost_0(aIWritingRequest)

Rewrite text for clarity or different tone.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.rewriteTextApiV1DocumentsDocumentIdAiRewritePost_0(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **rotatePdfPagesApiV1DocumentsDocumentIdPdfRotatePost**
> any rotatePdfPagesApiV1DocumentsDocumentIdPdfRotatePost(pDFRotateRequest)

Rotate pages in a PDF document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFRotateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFRotateRequest: PDFRotateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.rotatePdfPagesApiV1DocumentsDocumentIdPdfRotatePost(
    documentId,
    pDFRotateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFRotateRequest** | **PDFRotateRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **rotatePdfPagesApiV1DocumentsDocumentIdPdfRotatePost_0**
> any rotatePdfPagesApiV1DocumentsDocumentIdPdfRotatePost_0(pDFRotateRequest)

Rotate pages in a PDF document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFRotateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFRotateRequest: PDFRotateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.rotatePdfPagesApiV1DocumentsDocumentIdPdfRotatePost_0(
    documentId,
    pDFRotateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFRotateRequest** | **PDFRotateRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **saveAsTemplateApiV1DocumentsDocumentIdSaveAsTemplatePost**
> DocumentResponse saveAsTemplateApiV1DocumentsDocumentIdSaveAsTemplatePost()

Save a document as a template by duplicating it with is_template=True.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.saveAsTemplateApiV1DocumentsDocumentIdSaveAsTemplatePost(
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

**DocumentResponse**

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

# **saveAsTemplateApiV1DocumentsDocumentIdSaveAsTemplatePost_0**
> DocumentResponse saveAsTemplateApiV1DocumentsDocumentIdSaveAsTemplatePost_0()

Save a document as a template by duplicating it with is_template=True.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.saveAsTemplateApiV1DocumentsDocumentIdSaveAsTemplatePost_0(
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

**DocumentResponse**

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

# **splitPdfApiV1DocumentsDocumentIdPdfSplitPost**
> any splitPdfApiV1DocumentsDocumentIdPdfSplitPost(pDFSplitRequest)

Split a PDF document into multiple documents at specified pages.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFSplitRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFSplitRequest: PDFSplitRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.splitPdfApiV1DocumentsDocumentIdPdfSplitPost(
    documentId,
    pDFSplitRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFSplitRequest** | **PDFSplitRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **splitPdfApiV1DocumentsDocumentIdPdfSplitPost_0**
> any splitPdfApiV1DocumentsDocumentIdPdfSplitPost_0(pDFSplitRequest)

Split a PDF document into multiple documents at specified pages.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PDFSplitRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let pDFSplitRequest: PDFSplitRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.splitPdfApiV1DocumentsDocumentIdPdfSplitPost_0(
    documentId,
    pDFSplitRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pDFSplitRequest** | **PDFSplitRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **startCollaborationApiV1DocumentsDocumentIdCollaboratePost**
> CollaborationSessionResponse startCollaborationApiV1DocumentsDocumentIdCollaboratePost()

Start a collaboration session for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.startCollaborationApiV1DocumentsDocumentIdCollaboratePost(
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

**CollaborationSessionResponse**

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

# **startCollaborationApiV1DocumentsDocumentIdCollaboratePost_0**
> CollaborationSessionResponse startCollaborationApiV1DocumentsDocumentIdCollaboratePost_0()

Start a collaboration session for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.startCollaborationApiV1DocumentsDocumentIdCollaboratePost_0(
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

**CollaborationSessionResponse**

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

# **summarizeTextApiV1DocumentsDocumentIdAiSummarizePost**
> AIWritingResponse summarizeTextApiV1DocumentsDocumentIdAiSummarizePost(aIWritingRequest)

Summarize text content.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.summarizeTextApiV1DocumentsDocumentIdAiSummarizePost(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **summarizeTextApiV1DocumentsDocumentIdAiSummarizePost_0**
> AIWritingResponse summarizeTextApiV1DocumentsDocumentIdAiSummarizePost_0(aIWritingRequest)

Summarize text content.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.summarizeTextApiV1DocumentsDocumentIdAiSummarizePost_0(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **translateTextApiV1DocumentsDocumentIdAiTranslatePost**
> AIWritingResponse translateTextApiV1DocumentsDocumentIdAiTranslatePost(aIWritingRequest)

Translate text to another language.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.translateTextApiV1DocumentsDocumentIdAiTranslatePost(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **translateTextApiV1DocumentsDocumentIdAiTranslatePost_0**
> AIWritingResponse translateTextApiV1DocumentsDocumentIdAiTranslatePost_0(aIWritingRequest)

Translate text to another language.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    AIWritingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let aIWritingRequest: AIWritingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.translateTextApiV1DocumentsDocumentIdAiTranslatePost_0(
    documentId,
    aIWritingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIWritingRequest** | **AIWritingRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIWritingResponse**

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

# **updateDocumentApiV1DocumentsDocumentIdPut**
> DocumentResponse updateDocumentApiV1DocumentsDocumentIdPut(updateDocumentRequest)

Update a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    UpdateDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let updateDocumentRequest: UpdateDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateDocumentApiV1DocumentsDocumentIdPut(
    documentId,
    updateDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateDocumentRequest** | **UpdateDocumentRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentResponse**

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

# **updateDocumentApiV1DocumentsDocumentIdPut_0**
> DocumentResponse updateDocumentApiV1DocumentsDocumentIdPut_0(updateDocumentRequest)

Update a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    UpdateDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let updateDocumentRequest: UpdateDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateDocumentApiV1DocumentsDocumentIdPut_0(
    documentId,
    updateDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateDocumentRequest** | **UpdateDocumentRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DocumentResponse**

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

# **updateUserPresenceApiV1DocumentsDocumentIdPresencePut**
> any updateUserPresenceApiV1DocumentsDocumentIdPresencePut(presenceUpdateBody)

Update user presence (cursor position and selection) for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PresenceUpdateBody
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let presenceUpdateBody: PresenceUpdateBody; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateUserPresenceApiV1DocumentsDocumentIdPresencePut(
    documentId,
    presenceUpdateBody,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **presenceUpdateBody** | **PresenceUpdateBody**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **updateUserPresenceApiV1DocumentsDocumentIdPresencePut_0**
> any updateUserPresenceApiV1DocumentsDocumentIdPresencePut_0(presenceUpdateBody)

Update user presence (cursor position and selection) for a document.

### Example

```typescript
import {
    DocumentsApi,
    Configuration,
    PresenceUpdateBody
} from './api';

const configuration = new Configuration();
const apiInstance = new DocumentsApi(configuration);

let documentId: string; // (default to undefined)
let presenceUpdateBody: PresenceUpdateBody; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateUserPresenceApiV1DocumentsDocumentIdPresencePut_0(
    documentId,
    presenceUpdateBody,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **presenceUpdateBody** | **PresenceUpdateBody**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

