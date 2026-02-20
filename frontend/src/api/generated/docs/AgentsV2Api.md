# AgentsV2Api

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**cancelTaskApiV1AgentsV2TasksTaskIdCancelPost**](#canceltaskapiv1agentsv2taskstaskidcancelpost) | **POST** /api/v1/agents/v2/tasks/{task_id}/cancel | Cancel Task|
|[**getStatsApiV1AgentsV2StatsGet**](#getstatsapiv1agentsv2statsget) | **GET** /api/v1/agents/v2/stats | Get Statistics|
|[**getTaskApiV1AgentsV2TasksTaskIdGet**](#gettaskapiv1agentsv2taskstaskidget) | **GET** /api/v1/agents/v2/tasks/{task_id} | Get Task|
|[**getTaskEventsApiV1AgentsV2TasksTaskIdEventsGet**](#gettaskeventsapiv1agentsv2taskstaskideventsget) | **GET** /api/v1/agents/v2/tasks/{task_id}/events | Get Task Events|
|[**healthCheckApiV1AgentsV2HealthGet**](#healthcheckapiv1agentsv2healthget) | **GET** /api/v1/agents/v2/health | Health Check|
|[**listAgentTypesApiV1AgentsV2TypesGet**](#listagenttypesapiv1agentsv2typesget) | **GET** /api/v1/agents/v2/types | List Agent Types|
|[**listRepurposeFormatsApiV1AgentsV2FormatsRepurposeGet**](#listrepurposeformatsapiv1agentsv2formatsrepurposeget) | **GET** /api/v1/agents/v2/formats/repurpose | List Repurpose Formats|
|[**listTasksApiV1AgentsV2TasksGet**](#listtasksapiv1agentsv2tasksget) | **GET** /api/v1/agents/v2/tasks | List Tasks|
|[**retryTaskApiV1AgentsV2TasksTaskIdRetryPost**](#retrytaskapiv1agentsv2taskstaskidretrypost) | **POST** /api/v1/agents/v2/tasks/{task_id}/retry | Retry Task|
|[**runContentRepurposeAgentApiV1AgentsV2ContentRepurposePost**](#runcontentrepurposeagentapiv1agentsv2contentrepurposepost) | **POST** /api/v1/agents/v2/content-repurpose | Run Content Repurposing Agent|
|[**runDataAnalystAgentApiV1AgentsV2DataAnalystPost**](#rundataanalystagentapiv1agentsv2dataanalystpost) | **POST** /api/v1/agents/v2/data-analyst | Run Data Analyst Agent|
|[**runEmailDraftAgentApiV1AgentsV2EmailDraftPost**](#runemaildraftagentapiv1agentsv2emaildraftpost) | **POST** /api/v1/agents/v2/email-draft | Run Email Draft Agent|
|[**runProofreadingAgentApiV1AgentsV2ProofreadingPost**](#runproofreadingagentapiv1agentsv2proofreadingpost) | **POST** /api/v1/agents/v2/proofreading | Run Proofreading Agent|
|[**runResearchAgentApiV1AgentsV2ResearchPost**](#runresearchagentapiv1agentsv2researchpost) | **POST** /api/v1/agents/v2/research | Run Research Agent|
|[**streamTaskProgressApiV1AgentsV2TasksTaskIdStreamGet**](#streamtaskprogressapiv1agentsv2taskstaskidstreamget) | **GET** /api/v1/agents/v2/tasks/{task_id}/stream | Stream Task Progress (SSE)|

# **cancelTaskApiV1AgentsV2TasksTaskIdCancelPost**
> TaskResponse cancelTaskApiV1AgentsV2TasksTaskIdCancelPost()

Cancel a pending or running task. Cannot cancel completed tasks.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration,
    CancelRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let taskId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let cancelRequest: CancelRequest; // (optional)

const { status, data } = await apiInstance.cancelTaskApiV1AgentsV2TasksTaskIdCancelPost(
    taskId,
    xApiKey,
    cancelRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **cancelRequest** | **CancelRequest**|  | |
| **taskId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TaskResponse**

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

# **getStatsApiV1AgentsV2StatsGet**
> StatsResponse getStatsApiV1AgentsV2StatsGet()

Get task counts by status.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getStatsApiV1AgentsV2StatsGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**StatsResponse**

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

# **getTaskApiV1AgentsV2TasksTaskIdGet**
> TaskResponse getTaskApiV1AgentsV2TasksTaskIdGet()

Get a task by ID with full status, progress, and result information.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let taskId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTaskApiV1AgentsV2TasksTaskIdGet(
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

**TaskResponse**

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

# **getTaskEventsApiV1AgentsV2TasksTaskIdEventsGet**
> Array<TaskEventResponse> getTaskEventsApiV1AgentsV2TasksTaskIdEventsGet()

Get audit trail events for a task.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let taskId: string; // (default to undefined)
let limit: number; //Maximum number of events (optional) (default to 100)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTaskEventsApiV1AgentsV2TasksTaskIdEventsGet(
    taskId,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **taskId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] | Maximum number of events | (optional) defaults to 100|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TaskEventResponse>**

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

# **healthCheckApiV1AgentsV2HealthGet**
> any healthCheckApiV1AgentsV2HealthGet()

Check if the agents service is healthy.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.healthCheckApiV1AgentsV2HealthGet(
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

# **listAgentTypesApiV1AgentsV2TypesGet**
> any listAgentTypesApiV1AgentsV2TypesGet()

List available agent types with descriptions.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAgentTypesApiV1AgentsV2TypesGet(
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

# **listRepurposeFormatsApiV1AgentsV2FormatsRepurposeGet**
> any listRepurposeFormatsApiV1AgentsV2FormatsRepurposeGet()

List available content repurposing target formats with descriptions.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listRepurposeFormatsApiV1AgentsV2FormatsRepurposeGet(
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

# **listTasksApiV1AgentsV2TasksGet**
> TaskListResponse listTasksApiV1AgentsV2TasksGet()

List tasks with optional filtering by agent type, status, or user.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let agentType: string; //Filter by agent type (optional) (default to undefined)
let status: string; //Filter by status (optional) (default to undefined)
let userId: string; //Filter by user ID (optional) (default to undefined)
let limit: number; //Maximum number of tasks (optional) (default to 50)
let offset: number; //Number of tasks to skip (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTasksApiV1AgentsV2TasksGet(
    agentType,
    status,
    userId,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentType** | [**string**] | Filter by agent type | (optional) defaults to undefined|
| **status** | [**string**] | Filter by status | (optional) defaults to undefined|
| **userId** | [**string**] | Filter by user ID | (optional) defaults to undefined|
| **limit** | [**number**] | Maximum number of tasks | (optional) defaults to 50|
| **offset** | [**number**] | Number of tasks to skip | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TaskListResponse**

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

# **retryTaskApiV1AgentsV2TasksTaskIdRetryPost**
> TaskResponse retryTaskApiV1AgentsV2TasksTaskIdRetryPost()

Manually retry a failed task. Only works for retryable failures.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let taskId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.retryTaskApiV1AgentsV2TasksTaskIdRetryPost(
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

**TaskResponse**

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

# **runContentRepurposeAgentApiV1AgentsV2ContentRepurposePost**
> TaskResponse runContentRepurposeAgentApiV1AgentsV2ContentRepurposePost(backendAppApiRoutesAgentsV2ContentRepurposeRequest)

Transform content into multiple formats (tweets, LinkedIn, slides, newsletters, etc.).

### Example

```typescript
import {
    AgentsV2Api,
    Configuration,
    BackendAppApiRoutesAgentsV2ContentRepurposeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let backendAppApiRoutesAgentsV2ContentRepurposeRequest: BackendAppApiRoutesAgentsV2ContentRepurposeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runContentRepurposeAgentApiV1AgentsV2ContentRepurposePost(
    backendAppApiRoutesAgentsV2ContentRepurposeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesAgentsV2ContentRepurposeRequest** | **BackendAppApiRoutesAgentsV2ContentRepurposeRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TaskResponse**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **runDataAnalystAgentApiV1AgentsV2DataAnalystPost**
> TaskResponse runDataAnalystAgentApiV1AgentsV2DataAnalystPost(dataAnalystRequest)

Analyse tabular data: answer questions, compute statistics, suggest charts, generate SQL.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration,
    DataAnalystRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let dataAnalystRequest: DataAnalystRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runDataAnalystAgentApiV1AgentsV2DataAnalystPost(
    dataAnalystRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dataAnalystRequest** | **DataAnalystRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TaskResponse**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **runEmailDraftAgentApiV1AgentsV2EmailDraftPost**
> TaskResponse runEmailDraftAgentApiV1AgentsV2EmailDraftPost(backendAppApiRoutesAgentsV2EmailDraftRequest)

Compose email drafts with tone control, thread context, and follow-up actions.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration,
    BackendAppApiRoutesAgentsV2EmailDraftRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let backendAppApiRoutesAgentsV2EmailDraftRequest: BackendAppApiRoutesAgentsV2EmailDraftRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runEmailDraftAgentApiV1AgentsV2EmailDraftPost(
    backendAppApiRoutesAgentsV2EmailDraftRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesAgentsV2EmailDraftRequest** | **BackendAppApiRoutesAgentsV2EmailDraftRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TaskResponse**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **runProofreadingAgentApiV1AgentsV2ProofreadingPost**
> TaskResponse runProofreadingAgentApiV1AgentsV2ProofreadingPost(backendAppApiRoutesAgentsV2ProofreadingRequest)

Grammar, style, and clarity checking with style guide support and readability scoring.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration,
    BackendAppApiRoutesAgentsV2ProofreadingRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let backendAppApiRoutesAgentsV2ProofreadingRequest: BackendAppApiRoutesAgentsV2ProofreadingRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runProofreadingAgentApiV1AgentsV2ProofreadingPost(
    backendAppApiRoutesAgentsV2ProofreadingRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesAgentsV2ProofreadingRequest** | **BackendAppApiRoutesAgentsV2ProofreadingRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TaskResponse**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **runResearchAgentApiV1AgentsV2ResearchPost**
> TaskResponse runResearchAgentApiV1AgentsV2ResearchPost(backendAppApiRoutesAgentsV2ResearchRequest)

Run the research agent to compile a comprehensive report on a topic.      The agent will:     1. Generate a research outline based on the topic and depth     2. Research each section with relevant findings     3. Synthesize findings into a cohesive report with recommendations      **Idempotency**: Provide an `idempotency_key` to ensure the same request     doesn\'t create duplicate tasks. If a task with the same key exists,     it will be returned instead of creating a new one.      **Async Mode**: Set `sync=false` to return immediately with task ID.     Poll the task endpoint or use webhook for completion notification.

### Example

```typescript
import {
    AgentsV2Api,
    Configuration,
    BackendAppApiRoutesAgentsV2ResearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let backendAppApiRoutesAgentsV2ResearchRequest: BackendAppApiRoutesAgentsV2ResearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.runResearchAgentApiV1AgentsV2ResearchPost(
    backendAppApiRoutesAgentsV2ResearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesAgentsV2ResearchRequest** | **BackendAppApiRoutesAgentsV2ResearchRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TaskResponse**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Task created/returned successfully |  -  |
|**400** | Invalid input parameters |  -  |
|**422** | Validation Error |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **streamTaskProgressApiV1AgentsV2TasksTaskIdStreamGet**
> any streamTaskProgressApiV1AgentsV2TasksTaskIdStreamGet()

Stream real-time progress updates for a task using Server-Sent Events.      Returns an NDJSON stream of progress events. Each line is a JSON object     with `event` and `data` fields. The stream terminates when the task     reaches a terminal state (completed, failed, cancelled) or the timeout     is reached.      **Content-Type**: `text/event-stream`      **Events**:     - `progress`: Task progress update with percent, message, step info     - `complete`: Task reached terminal state (includes result or error)     - `error`: An error occurred (task not found, stream timeout)      **Example usage** (JavaScript):     ```js     const eventSource = new EventSource(\'/agents/v2/tasks/abc123/stream\');     eventSource.onmessage = (e) => {       const data = JSON.parse(e.data);       console.log(data.event, data.data);     };     ```

### Example

```typescript
import {
    AgentsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AgentsV2Api(configuration);

let taskId: string; // (default to undefined)
let pollInterval: number; //Poll interval in seconds (optional) (default to 0.5)
let timeout: number; //Stream timeout in seconds (optional) (default to 300.0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.streamTaskProgressApiV1AgentsV2TasksTaskIdStreamGet(
    taskId,
    pollInterval,
    timeout,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **taskId** | [**string**] |  | defaults to undefined|
| **pollInterval** | [**number**] | Poll interval in seconds | (optional) defaults to 0.5|
| **timeout** | [**number**] | Stream timeout in seconds | (optional) defaults to 300.0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/event-stream


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | SSE progress stream |  -  |
|**404** | Task not found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

