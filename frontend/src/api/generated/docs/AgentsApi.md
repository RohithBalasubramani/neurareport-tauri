# AgentsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getTaskApiV1AgentsTasksTaskIdGet**](#gettaskapiv1agentstaskstaskidget) | **GET** /api/v1/agents/tasks/{task_id} | Get Task|
|[**listAgentTypesApiV1AgentsTypesGet**](#listagenttypesapiv1agentstypesget) | **GET** /api/v1/agents/types | List Agent Types|
|[**listRepurposeFormatsApiV1AgentsFormatsRepurposeGet**](#listrepurposeformatsapiv1agentsformatsrepurposeget) | **GET** /api/v1/agents/formats/repurpose | List Repurpose Formats|
|[**listTasksApiV1AgentsTasksGet**](#listtasksapiv1agentstasksget) | **GET** /api/v1/agents/tasks | List Tasks|
|[**runContentRepurposingAgentApiV1AgentsContentRepurposePost**](#runcontentrepurposingagentapiv1agentscontentrepurposepost) | **POST** /api/v1/agents/content-repurpose | Run Content Repurposing Agent|
|[**runDataAnalystAgentApiV1AgentsDataAnalysisPost**](#rundataanalystagentapiv1agentsdataanalysispost) | **POST** /api/v1/agents/data-analysis | Run Data Analyst Agent|
|[**runEmailDraftAgentApiV1AgentsEmailDraftPost**](#runemaildraftagentapiv1agentsemaildraftpost) | **POST** /api/v1/agents/email-draft | Run Email Draft Agent|
|[**runProofreadingAgentApiV1AgentsProofreadPost**](#runproofreadingagentapiv1agentsproofreadpost) | **POST** /api/v1/agents/proofread | Run Proofreading Agent|
|[**runResearchAgentApiV1AgentsResearchPost**](#runresearchagentapiv1agentsresearchpost) | **POST** /api/v1/agents/research | Run Research Agent|

# **getTaskApiV1AgentsTasksTaskIdGet**
> any getTaskApiV1AgentsTasksTaskIdGet()

Get task by ID.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let taskId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTaskApiV1AgentsTasksTaskIdGet(
    taskId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **taskId** | [**string**] |  | defaults to undefined|
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

# **listAgentTypesApiV1AgentsTypesGet**
> any listAgentTypesApiV1AgentsTypesGet()

List available agent types.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAgentTypesApiV1AgentsTypesGet(
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

# **listRepurposeFormatsApiV1AgentsFormatsRepurposeGet**
> any listRepurposeFormatsApiV1AgentsFormatsRepurposeGet()

List available content repurposing formats.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listRepurposeFormatsApiV1AgentsFormatsRepurposeGet(
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

# **listTasksApiV1AgentsTasksGet**
> any listTasksApiV1AgentsTasksGet()

List all tasks, optionally filtered by agent type.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentType: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTasksApiV1AgentsTasksGet(
    agentType,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentType** | [**string**] |  | (optional) defaults to undefined|
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

# **runContentRepurposingAgentApiV1AgentsContentRepurposePost**
> any runContentRepurposingAgentApiV1AgentsContentRepurposePost(backendAppApiRoutesAgentsContentRepurposeRequest)

Run the content repurposing agent to transform content.  Returns:     RepurposedContent with all versions

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    BackendAppApiRoutesAgentsContentRepurposeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let backendAppApiRoutesAgentsContentRepurposeRequest: BackendAppApiRoutesAgentsContentRepurposeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runContentRepurposingAgentApiV1AgentsContentRepurposePost(
    backendAppApiRoutesAgentsContentRepurposeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesAgentsContentRepurposeRequest** | **BackendAppApiRoutesAgentsContentRepurposeRequest**|  | |
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

# **runDataAnalystAgentApiV1AgentsDataAnalysisPost**
> any runDataAnalystAgentApiV1AgentsDataAnalysisPost(dataAnalysisRequest)

Run the data analyst agent to answer questions about data.  Returns:     DataAnalysisResult with insights

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    DataAnalysisRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let dataAnalysisRequest: DataAnalysisRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runDataAnalystAgentApiV1AgentsDataAnalysisPost(
    dataAnalysisRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dataAnalysisRequest** | **DataAnalysisRequest**|  | |
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

# **runEmailDraftAgentApiV1AgentsEmailDraftPost**
> any runEmailDraftAgentApiV1AgentsEmailDraftPost(backendAppApiRoutesAgentsEmailDraftRequest)

Run the email draft agent to compose an email.  Returns:     EmailDraft with composed email

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    BackendAppApiRoutesAgentsEmailDraftRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let backendAppApiRoutesAgentsEmailDraftRequest: BackendAppApiRoutesAgentsEmailDraftRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runEmailDraftAgentApiV1AgentsEmailDraftPost(
    backendAppApiRoutesAgentsEmailDraftRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesAgentsEmailDraftRequest** | **BackendAppApiRoutesAgentsEmailDraftRequest**|  | |
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

# **runProofreadingAgentApiV1AgentsProofreadPost**
> any runProofreadingAgentApiV1AgentsProofreadPost(backendAppApiRoutesAgentsProofreadingRequest)

Run the proofreading agent for comprehensive style and grammar check.  Returns:     ProofreadingResult with corrections

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    BackendAppApiRoutesAgentsProofreadingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let backendAppApiRoutesAgentsProofreadingRequest: BackendAppApiRoutesAgentsProofreadingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runProofreadingAgentApiV1AgentsProofreadPost(
    backendAppApiRoutesAgentsProofreadingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesAgentsProofreadingRequest** | **BackendAppApiRoutesAgentsProofreadingRequest**|  | |
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

# **runResearchAgentApiV1AgentsResearchPost**
> any runResearchAgentApiV1AgentsResearchPost(backendAppApiRoutesAgentsResearchRequest)

Run the research agent to compile a report on a topic.  Returns:     ResearchReport with findings

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    BackendAppApiRoutesAgentsResearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let backendAppApiRoutesAgentsResearchRequest: BackendAppApiRoutesAgentsResearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runResearchAgentApiV1AgentsResearchPost(
    backendAppApiRoutesAgentsResearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesAgentsResearchRequest** | **BackendAppApiRoutesAgentsResearchRequest**|  | |
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

