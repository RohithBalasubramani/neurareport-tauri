# DocqaApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addDocumentApiV1DocqaSessionsSessionIdDocumentsPost**](#adddocumentapiv1docqasessionssessioniddocumentspost) | **POST** /api/v1/docqa/sessions/{session_id}/documents | Add Document|
|[**askQuestionApiV1DocqaSessionsSessionIdAskPost**](#askquestionapiv1docqasessionssessionidaskpost) | **POST** /api/v1/docqa/sessions/{session_id}/ask | Ask Question|
|[**clearChatHistoryApiV1DocqaSessionsSessionIdHistoryDelete**](#clearchathistoryapiv1docqasessionssessionidhistorydelete) | **DELETE** /api/v1/docqa/sessions/{session_id}/history | Clear Chat History|
|[**createSessionApiV1DocqaSessionsPost**](#createsessionapiv1docqasessionspost) | **POST** /api/v1/docqa/sessions | Create Session|
|[**deleteSessionApiV1DocqaSessionsSessionIdDelete**](#deletesessionapiv1docqasessionssessioniddelete) | **DELETE** /api/v1/docqa/sessions/{session_id} | Delete Session|
|[**getChatHistoryApiV1DocqaSessionsSessionIdHistoryGet**](#getchathistoryapiv1docqasessionssessionidhistoryget) | **GET** /api/v1/docqa/sessions/{session_id}/history | Get Chat History|
|[**getSessionApiV1DocqaSessionsSessionIdGet**](#getsessionapiv1docqasessionssessionidget) | **GET** /api/v1/docqa/sessions/{session_id} | Get Session|
|[**listSessionsApiV1DocqaSessionsGet**](#listsessionsapiv1docqasessionsget) | **GET** /api/v1/docqa/sessions | List Sessions|
|[**regenerateResponseApiV1DocqaSessionsSessionIdMessagesMessageIdRegeneratePost**](#regenerateresponseapiv1docqasessionssessionidmessagesmessageidregeneratepost) | **POST** /api/v1/docqa/sessions/{session_id}/messages/{message_id}/regenerate | Regenerate Response|
|[**removeDocumentApiV1DocqaSessionsSessionIdDocumentsDocumentIdDelete**](#removedocumentapiv1docqasessionssessioniddocumentsdocumentiddelete) | **DELETE** /api/v1/docqa/sessions/{session_id}/documents/{document_id} | Remove Document|
|[**submitFeedbackApiV1DocqaSessionsSessionIdMessagesMessageIdFeedbackPost**](#submitfeedbackapiv1docqasessionssessionidmessagesmessageidfeedbackpost) | **POST** /api/v1/docqa/sessions/{session_id}/messages/{message_id}/feedback | Submit Feedback|

# **addDocumentApiV1DocqaSessionsSessionIdDocumentsPost**
> any addDocumentApiV1DocqaSessionsSessionIdDocumentsPost(backendAppApiRoutesDocqaAddDocumentRequest)

Add a document to a Q&A session.

### Example

```typescript
import {
    DocqaApi,
    Configuration,
    BackendAppApiRoutesDocqaAddDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let backendAppApiRoutesDocqaAddDocumentRequest: BackendAppApiRoutesDocqaAddDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDocumentApiV1DocqaSessionsSessionIdDocumentsPost(
    sessionId,
    backendAppApiRoutesDocqaAddDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesDocqaAddDocumentRequest** | **BackendAppApiRoutesDocqaAddDocumentRequest**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
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

# **askQuestionApiV1DocqaSessionsSessionIdAskPost**
> any askQuestionApiV1DocqaSessionsSessionIdAskPost(askRequest)

Ask a question about the documents in a session.

### Example

```typescript
import {
    DocqaApi,
    Configuration,
    AskRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let askRequest: AskRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.askQuestionApiV1DocqaSessionsSessionIdAskPost(
    sessionId,
    askRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **askRequest** | **AskRequest**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
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

# **clearChatHistoryApiV1DocqaSessionsSessionIdHistoryDelete**
> any clearChatHistoryApiV1DocqaSessionsSessionIdHistoryDelete()

Clear chat history for a session.

### Example

```typescript
import {
    DocqaApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.clearChatHistoryApiV1DocqaSessionsSessionIdHistoryDelete(
    sessionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
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

# **createSessionApiV1DocqaSessionsPost**
> any createSessionApiV1DocqaSessionsPost(backendAppApiRoutesDocqaCreateSessionRequest)

Create a new Q&A session.

### Example

```typescript
import {
    DocqaApi,
    Configuration,
    BackendAppApiRoutesDocqaCreateSessionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let backendAppApiRoutesDocqaCreateSessionRequest: BackendAppApiRoutesDocqaCreateSessionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSessionApiV1DocqaSessionsPost(
    backendAppApiRoutesDocqaCreateSessionRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesDocqaCreateSessionRequest** | **BackendAppApiRoutesDocqaCreateSessionRequest**|  | |
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

# **deleteSessionApiV1DocqaSessionsSessionIdDelete**
> any deleteSessionApiV1DocqaSessionsSessionIdDelete()

Delete a Q&A session.

### Example

```typescript
import {
    DocqaApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSessionApiV1DocqaSessionsSessionIdDelete(
    sessionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
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

# **getChatHistoryApiV1DocqaSessionsSessionIdHistoryGet**
> any getChatHistoryApiV1DocqaSessionsSessionIdHistoryGet()

Get chat history for a session.

### Example

```typescript
import {
    DocqaApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let limit: number; // (optional) (default to 50)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getChatHistoryApiV1DocqaSessionsSessionIdHistoryGet(
    sessionId,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
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

# **getSessionApiV1DocqaSessionsSessionIdGet**
> any getSessionApiV1DocqaSessionsSessionIdGet()

Get a Q&A session by ID.

### Example

```typescript
import {
    DocqaApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionApiV1DocqaSessionsSessionIdGet(
    sessionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
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

# **listSessionsApiV1DocqaSessionsGet**
> any listSessionsApiV1DocqaSessionsGet()

List all Q&A sessions.

### Example

```typescript
import {
    DocqaApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSessionsApiV1DocqaSessionsGet(
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
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

# **regenerateResponseApiV1DocqaSessionsSessionIdMessagesMessageIdRegeneratePost**
> any regenerateResponseApiV1DocqaSessionsSessionIdMessagesMessageIdRegeneratePost(regenerateRequest)

Regenerate a response for a message.

### Example

```typescript
import {
    DocqaApi,
    Configuration,
    RegenerateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let messageId: string; // (default to undefined)
let regenerateRequest: RegenerateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.regenerateResponseApiV1DocqaSessionsSessionIdMessagesMessageIdRegeneratePost(
    sessionId,
    messageId,
    regenerateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **regenerateRequest** | **RegenerateRequest**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **messageId** | [**string**] |  | defaults to undefined|
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

# **removeDocumentApiV1DocqaSessionsSessionIdDocumentsDocumentIdDelete**
> any removeDocumentApiV1DocqaSessionsSessionIdDocumentsDocumentIdDelete()

Remove a document from a session.

### Example

```typescript
import {
    DocqaApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeDocumentApiV1DocqaSessionsSessionIdDocumentsDocumentIdDelete(
    sessionId,
    documentId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
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

# **submitFeedbackApiV1DocqaSessionsSessionIdMessagesMessageIdFeedbackPost**
> any submitFeedbackApiV1DocqaSessionsSessionIdMessagesMessageIdFeedbackPost(feedbackRequest)

Submit feedback for a chat message.

### Example

```typescript
import {
    DocqaApi,
    Configuration,
    FeedbackRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocqaApi(configuration);

let sessionId: string; // (default to undefined)
let messageId: string; // (default to undefined)
let feedbackRequest: FeedbackRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.submitFeedbackApiV1DocqaSessionsSessionIdMessagesMessageIdFeedbackPost(
    sessionId,
    messageId,
    feedbackRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **feedbackRequest** | **FeedbackRequest**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **messageId** | [**string**] |  | defaults to undefined|
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

