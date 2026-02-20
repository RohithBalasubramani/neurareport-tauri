# SynthesisApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addDocumentApiV1SynthesisSessionsSessionIdDocumentsPost**](#adddocumentapiv1synthesissessionssessioniddocumentspost) | **POST** /api/v1/synthesis/sessions/{session_id}/documents | Add Document|
|[**createSessionApiV1SynthesisSessionsPost**](#createsessionapiv1synthesissessionspost) | **POST** /api/v1/synthesis/sessions | Create Session|
|[**deleteSessionApiV1SynthesisSessionsSessionIdDelete**](#deletesessionapiv1synthesissessionssessioniddelete) | **DELETE** /api/v1/synthesis/sessions/{session_id} | Delete Session|
|[**findInconsistenciesApiV1SynthesisSessionsSessionIdInconsistenciesGet**](#findinconsistenciesapiv1synthesissessionssessionidinconsistenciesget) | **GET** /api/v1/synthesis/sessions/{session_id}/inconsistencies | Find Inconsistencies|
|[**getSessionApiV1SynthesisSessionsSessionIdGet**](#getsessionapiv1synthesissessionssessionidget) | **GET** /api/v1/synthesis/sessions/{session_id} | Get Session|
|[**listSessionsApiV1SynthesisSessionsGet**](#listsessionsapiv1synthesissessionsget) | **GET** /api/v1/synthesis/sessions | List Sessions|
|[**removeDocumentApiV1SynthesisSessionsSessionIdDocumentsDocumentIdDelete**](#removedocumentapiv1synthesissessionssessioniddocumentsdocumentiddelete) | **DELETE** /api/v1/synthesis/sessions/{session_id}/documents/{document_id} | Remove Document|
|[**synthesizeDocumentsApiV1SynthesisSessionsSessionIdSynthesizePost**](#synthesizedocumentsapiv1synthesissessionssessionidsynthesizepost) | **POST** /api/v1/synthesis/sessions/{session_id}/synthesize | Synthesize Documents|

# **addDocumentApiV1SynthesisSessionsSessionIdDocumentsPost**
> any addDocumentApiV1SynthesisSessionsSessionIdDocumentsPost(backendAppApiRoutesSynthesisAddDocumentRequest)

Add a document to a synthesis session.

### Example

```typescript
import {
    SynthesisApi,
    Configuration,
    BackendAppApiRoutesSynthesisAddDocumentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SynthesisApi(configuration);

let sessionId: string; // (default to undefined)
let backendAppApiRoutesSynthesisAddDocumentRequest: BackendAppApiRoutesSynthesisAddDocumentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDocumentApiV1SynthesisSessionsSessionIdDocumentsPost(
    sessionId,
    backendAppApiRoutesSynthesisAddDocumentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesSynthesisAddDocumentRequest** | **BackendAppApiRoutesSynthesisAddDocumentRequest**|  | |
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

# **createSessionApiV1SynthesisSessionsPost**
> any createSessionApiV1SynthesisSessionsPost(backendAppApiRoutesDocqaCreateSessionRequest)

Create a new synthesis session.

### Example

```typescript
import {
    SynthesisApi,
    Configuration,
    BackendAppApiRoutesDocqaCreateSessionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SynthesisApi(configuration);

let backendAppApiRoutesDocqaCreateSessionRequest: BackendAppApiRoutesDocqaCreateSessionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSessionApiV1SynthesisSessionsPost(
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

# **deleteSessionApiV1SynthesisSessionsSessionIdDelete**
> any deleteSessionApiV1SynthesisSessionsSessionIdDelete()

Delete a synthesis session.

### Example

```typescript
import {
    SynthesisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SynthesisApi(configuration);

let sessionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSessionApiV1SynthesisSessionsSessionIdDelete(
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

# **findInconsistenciesApiV1SynthesisSessionsSessionIdInconsistenciesGet**
> any findInconsistenciesApiV1SynthesisSessionsSessionIdInconsistenciesGet()

Find inconsistencies between documents in a session.

### Example

```typescript
import {
    SynthesisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SynthesisApi(configuration);

let sessionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.findInconsistenciesApiV1SynthesisSessionsSessionIdInconsistenciesGet(
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

# **getSessionApiV1SynthesisSessionsSessionIdGet**
> any getSessionApiV1SynthesisSessionsSessionIdGet()

Get a synthesis session by ID.

### Example

```typescript
import {
    SynthesisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SynthesisApi(configuration);

let sessionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionApiV1SynthesisSessionsSessionIdGet(
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

# **listSessionsApiV1SynthesisSessionsGet**
> any listSessionsApiV1SynthesisSessionsGet()

List all synthesis sessions.

### Example

```typescript
import {
    SynthesisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SynthesisApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSessionsApiV1SynthesisSessionsGet(
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

# **removeDocumentApiV1SynthesisSessionsSessionIdDocumentsDocumentIdDelete**
> any removeDocumentApiV1SynthesisSessionsSessionIdDocumentsDocumentIdDelete()

Remove a document from a session.

### Example

```typescript
import {
    SynthesisApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SynthesisApi(configuration);

let sessionId: string; // (default to undefined)
let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeDocumentApiV1SynthesisSessionsSessionIdDocumentsDocumentIdDelete(
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

# **synthesizeDocumentsApiV1SynthesisSessionsSessionIdSynthesizePost**
> any synthesizeDocumentsApiV1SynthesisSessionsSessionIdSynthesizePost(synthesisRequest)

Synthesize information from all documents in a session.

### Example

```typescript
import {
    SynthesisApi,
    Configuration,
    SynthesisRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SynthesisApi(configuration);

let sessionId: string; // (default to undefined)
let synthesisRequest: SynthesisRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.synthesizeDocumentsApiV1SynthesisSessionsSessionIdSynthesizePost(
    sessionId,
    synthesisRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **synthesisRequest** | **SynthesisRequest**|  | |
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

