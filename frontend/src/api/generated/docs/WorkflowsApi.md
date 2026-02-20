# WorkflowsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**approveExecutionApiV1WorkflowsExecutionsExecutionIdApprovePost**](#approveexecutionapiv1workflowsexecutionsexecutionidapprovepost) | **POST** /api/v1/workflows/executions/{execution_id}/approve | Approve Execution|
|[**approveExecutionApiV1WorkflowsExecutionsExecutionIdApprovePost_0**](#approveexecutionapiv1workflowsexecutionsexecutionidapprovepost_0) | **POST** /api/v1/workflows/executions/{execution_id}/approve | Approve Execution|
|[**cancelExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdCancelPost**](#cancelexecutionapiv1workflowsworkflowidexecutionsexecutionidcancelpost) | **POST** /api/v1/workflows/{workflow_id}/executions/{execution_id}/cancel | Cancel Execution|
|[**cancelExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdCancelPost_0**](#cancelexecutionapiv1workflowsworkflowidexecutionsexecutionidcancelpost_0) | **POST** /api/v1/workflows/{workflow_id}/executions/{execution_id}/cancel | Cancel Execution|
|[**configureTriggerApiV1WorkflowsWorkflowIdTriggerPost**](#configuretriggerapiv1workflowsworkflowidtriggerpost) | **POST** /api/v1/workflows/{workflow_id}/trigger | Configure Trigger|
|[**configureTriggerApiV1WorkflowsWorkflowIdTriggerPost_0**](#configuretriggerapiv1workflowsworkflowidtriggerpost_0) | **POST** /api/v1/workflows/{workflow_id}/trigger | Configure Trigger|
|[**createWebhookApiV1WorkflowsWorkflowIdWebhooksPost**](#createwebhookapiv1workflowsworkflowidwebhookspost) | **POST** /api/v1/workflows/{workflow_id}/webhooks | Create Webhook|
|[**createWebhookApiV1WorkflowsWorkflowIdWebhooksPost_0**](#createwebhookapiv1workflowsworkflowidwebhookspost_0) | **POST** /api/v1/workflows/{workflow_id}/webhooks | Create Webhook|
|[**createWorkflowApiV1WorkflowsPost**](#createworkflowapiv1workflowspost) | **POST** /api/v1/workflows | Create Workflow|
|[**createWorkflowApiV1WorkflowsPost_0**](#createworkflowapiv1workflowspost_0) | **POST** /api/v1/workflows | Create Workflow|
|[**createWorkflowFromTemplateApiV1WorkflowsTemplatesTemplateIdCreatePost**](#createworkflowfromtemplateapiv1workflowstemplatestemplateidcreatepost) | **POST** /api/v1/workflows/templates/{template_id}/create | Create Workflow From Template|
|[**createWorkflowFromTemplateApiV1WorkflowsTemplatesTemplateIdCreatePost_0**](#createworkflowfromtemplateapiv1workflowstemplatestemplateidcreatepost_0) | **POST** /api/v1/workflows/templates/{template_id}/create | Create Workflow From Template|
|[**debugWorkflowApiV1WorkflowsWorkflowIdDebugPost**](#debugworkflowapiv1workflowsworkflowiddebugpost) | **POST** /api/v1/workflows/{workflow_id}/debug | Debug Workflow|
|[**debugWorkflowApiV1WorkflowsWorkflowIdDebugPost_0**](#debugworkflowapiv1workflowsworkflowiddebugpost_0) | **POST** /api/v1/workflows/{workflow_id}/debug | Debug Workflow|
|[**deleteTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDelete**](#deletetriggerapiv1workflowsworkflowidtriggerstriggeriddelete) | **DELETE** /api/v1/workflows/{workflow_id}/triggers/{trigger_id} | Delete Trigger|
|[**deleteTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDelete_0**](#deletetriggerapiv1workflowsworkflowidtriggerstriggeriddelete_0) | **DELETE** /api/v1/workflows/{workflow_id}/triggers/{trigger_id} | Delete Trigger|
|[**deleteWebhookApiV1WorkflowsWorkflowIdWebhooksWebhookIdDelete**](#deletewebhookapiv1workflowsworkflowidwebhookswebhookiddelete) | **DELETE** /api/v1/workflows/{workflow_id}/webhooks/{webhook_id} | Delete Webhook|
|[**deleteWebhookApiV1WorkflowsWorkflowIdWebhooksWebhookIdDelete_0**](#deletewebhookapiv1workflowsworkflowidwebhookswebhookiddelete_0) | **DELETE** /api/v1/workflows/{workflow_id}/webhooks/{webhook_id} | Delete Webhook|
|[**deleteWorkflowApiV1WorkflowsWorkflowIdDelete**](#deleteworkflowapiv1workflowsworkflowiddelete) | **DELETE** /api/v1/workflows/{workflow_id} | Delete Workflow|
|[**deleteWorkflowApiV1WorkflowsWorkflowIdDelete_0**](#deleteworkflowapiv1workflowsworkflowiddelete_0) | **DELETE** /api/v1/workflows/{workflow_id} | Delete Workflow|
|[**disableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDisablePost**](#disabletriggerapiv1workflowsworkflowidtriggerstriggeriddisablepost) | **POST** /api/v1/workflows/{workflow_id}/triggers/{trigger_id}/disable | Disable Trigger|
|[**disableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDisablePost_0**](#disabletriggerapiv1workflowsworkflowidtriggerstriggeriddisablepost_0) | **POST** /api/v1/workflows/{workflow_id}/triggers/{trigger_id}/disable | Disable Trigger|
|[**enableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdEnablePost**](#enabletriggerapiv1workflowsworkflowidtriggerstriggeridenablepost) | **POST** /api/v1/workflows/{workflow_id}/triggers/{trigger_id}/enable | Enable Trigger|
|[**enableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdEnablePost_0**](#enabletriggerapiv1workflowsworkflowidtriggerstriggeridenablepost_0) | **POST** /api/v1/workflows/{workflow_id}/triggers/{trigger_id}/enable | Enable Trigger|
|[**executeWorkflowApiV1WorkflowsWorkflowIdExecutePost**](#executeworkflowapiv1workflowsworkflowidexecutepost) | **POST** /api/v1/workflows/{workflow_id}/execute | Execute Workflow|
|[**executeWorkflowApiV1WorkflowsWorkflowIdExecutePost_0**](#executeworkflowapiv1workflowsworkflowidexecutepost_0) | **POST** /api/v1/workflows/{workflow_id}/execute | Execute Workflow|
|[**getExecutionApiV1WorkflowsExecutionsExecutionIdGet**](#getexecutionapiv1workflowsexecutionsexecutionidget) | **GET** /api/v1/workflows/executions/{execution_id} | Get Execution|
|[**getExecutionApiV1WorkflowsExecutionsExecutionIdGet_0**](#getexecutionapiv1workflowsexecutionsexecutionidget_0) | **GET** /api/v1/workflows/executions/{execution_id} | Get Execution|
|[**getExecutionLogsApiV1WorkflowsWorkflowIdExecutionsExecutionIdLogsGet**](#getexecutionlogsapiv1workflowsworkflowidexecutionsexecutionidlogsget) | **GET** /api/v1/workflows/{workflow_id}/executions/{execution_id}/logs | Get Execution Logs|
|[**getExecutionLogsApiV1WorkflowsWorkflowIdExecutionsExecutionIdLogsGet_0**](#getexecutionlogsapiv1workflowsworkflowidexecutionsexecutionidlogsget_0) | **GET** /api/v1/workflows/{workflow_id}/executions/{execution_id}/logs | Get Execution Logs|
|[**getNodeTypeSchemaApiV1WorkflowsNodeTypesNodeTypeSchemaGet**](#getnodetypeschemaapiv1workflowsnodetypesnodetypeschemaget) | **GET** /api/v1/workflows/node-types/{node_type}/schema | Get Node Type Schema|
|[**getNodeTypeSchemaApiV1WorkflowsNodeTypesNodeTypeSchemaGet_0**](#getnodetypeschemaapiv1workflowsnodetypesnodetypeschemaget_0) | **GET** /api/v1/workflows/node-types/{node_type}/schema | Get Node Type Schema|
|[**getPendingApprovalsApiV1WorkflowsApprovalsPendingGet**](#getpendingapprovalsapiv1workflowsapprovalspendingget) | **GET** /api/v1/workflows/approvals/pending | Get Pending Approvals|
|[**getPendingApprovalsApiV1WorkflowsApprovalsPendingGet_0**](#getpendingapprovalsapiv1workflowsapprovalspendingget_0) | **GET** /api/v1/workflows/approvals/pending | Get Pending Approvals|
|[**getWorkflowApiV1WorkflowsWorkflowIdGet**](#getworkflowapiv1workflowsworkflowidget) | **GET** /api/v1/workflows/{workflow_id} | Get Workflow|
|[**getWorkflowApiV1WorkflowsWorkflowIdGet_0**](#getworkflowapiv1workflowsworkflowidget_0) | **GET** /api/v1/workflows/{workflow_id} | Get Workflow|
|[**listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet**](#listexecutionsapiv1workflowsworkflowidexecutionsget) | **GET** /api/v1/workflows/{workflow_id}/executions | List Executions|
|[**listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet_0**](#listexecutionsapiv1workflowsworkflowidexecutionsget_0) | **GET** /api/v1/workflows/{workflow_id}/executions | List Executions|
|[**listNodeTypesApiV1WorkflowsNodeTypesGet**](#listnodetypesapiv1workflowsnodetypesget) | **GET** /api/v1/workflows/node-types | List Node Types|
|[**listNodeTypesApiV1WorkflowsNodeTypesGet_0**](#listnodetypesapiv1workflowsnodetypesget_0) | **GET** /api/v1/workflows/node-types | List Node Types|
|[**listWebhooksApiV1WorkflowsWorkflowIdWebhooksGet**](#listwebhooksapiv1workflowsworkflowidwebhooksget) | **GET** /api/v1/workflows/{workflow_id}/webhooks | List Webhooks|
|[**listWebhooksApiV1WorkflowsWorkflowIdWebhooksGet_0**](#listwebhooksapiv1workflowsworkflowidwebhooksget_0) | **GET** /api/v1/workflows/{workflow_id}/webhooks | List Webhooks|
|[**listWorkflowTemplatesApiV1WorkflowsTemplatesGet**](#listworkflowtemplatesapiv1workflowstemplatesget) | **GET** /api/v1/workflows/templates | List Workflow Templates|
|[**listWorkflowTemplatesApiV1WorkflowsTemplatesGet_0**](#listworkflowtemplatesapiv1workflowstemplatesget_0) | **GET** /api/v1/workflows/templates | List Workflow Templates|
|[**listWorkflowsApiV1WorkflowsGet**](#listworkflowsapiv1workflowsget) | **GET** /api/v1/workflows | List Workflows|
|[**listWorkflowsApiV1WorkflowsGet_0**](#listworkflowsapiv1workflowsget_0) | **GET** /api/v1/workflows | List Workflows|
|[**regenerateWebhookSecretApiV1WorkflowsWorkflowIdWebhooksWebhookIdRegenerateSecretPost**](#regeneratewebhooksecretapiv1workflowsworkflowidwebhookswebhookidregeneratesecretpost) | **POST** /api/v1/workflows/{workflow_id}/webhooks/{webhook_id}/regenerate-secret | Regenerate Webhook Secret|
|[**regenerateWebhookSecretApiV1WorkflowsWorkflowIdWebhooksWebhookIdRegenerateSecretPost_0**](#regeneratewebhooksecretapiv1workflowsworkflowidwebhookswebhookidregeneratesecretpost_0) | **POST** /api/v1/workflows/{workflow_id}/webhooks/{webhook_id}/regenerate-secret | Regenerate Webhook Secret|
|[**retryExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdRetryPost**](#retryexecutionapiv1workflowsworkflowidexecutionsexecutionidretrypost) | **POST** /api/v1/workflows/{workflow_id}/executions/{execution_id}/retry | Retry Execution|
|[**retryExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdRetryPost_0**](#retryexecutionapiv1workflowsworkflowidexecutionsexecutionidretrypost_0) | **POST** /api/v1/workflows/{workflow_id}/executions/{execution_id}/retry | Retry Execution|
|[**saveAsTemplateApiV1WorkflowsWorkflowIdSaveAsTemplatePost**](#saveastemplateapiv1workflowsworkflowidsaveastemplatepost) | **POST** /api/v1/workflows/{workflow_id}/save-as-template | Save As Template|
|[**saveAsTemplateApiV1WorkflowsWorkflowIdSaveAsTemplatePost_0**](#saveastemplateapiv1workflowsworkflowidsaveastemplatepost_0) | **POST** /api/v1/workflows/{workflow_id}/save-as-template | Save As Template|
|[**updateTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdPut**](#updatetriggerapiv1workflowsworkflowidtriggerstriggeridput) | **PUT** /api/v1/workflows/{workflow_id}/triggers/{trigger_id} | Update Trigger|
|[**updateTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdPut_0**](#updatetriggerapiv1workflowsworkflowidtriggerstriggeridput_0) | **PUT** /api/v1/workflows/{workflow_id}/triggers/{trigger_id} | Update Trigger|
|[**updateWorkflowApiV1WorkflowsWorkflowIdPut**](#updateworkflowapiv1workflowsworkflowidput) | **PUT** /api/v1/workflows/{workflow_id} | Update Workflow|
|[**updateWorkflowApiV1WorkflowsWorkflowIdPut_0**](#updateworkflowapiv1workflowsworkflowidput_0) | **PUT** /api/v1/workflows/{workflow_id} | Update Workflow|

# **approveExecutionApiV1WorkflowsExecutionsExecutionIdApprovePost**
> any approveExecutionApiV1WorkflowsExecutionsExecutionIdApprovePost(approvalRequest)

Approve or reject a pending approval.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    ApprovalRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let executionId: string; // (default to undefined)
let approvalRequest: ApprovalRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.approveExecutionApiV1WorkflowsExecutionsExecutionIdApprovePost(
    executionId,
    approvalRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **approvalRequest** | **ApprovalRequest**|  | |
| **executionId** | [**string**] |  | defaults to undefined|
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

# **approveExecutionApiV1WorkflowsExecutionsExecutionIdApprovePost_0**
> any approveExecutionApiV1WorkflowsExecutionsExecutionIdApprovePost_0(approvalRequest)

Approve or reject a pending approval.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    ApprovalRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let executionId: string; // (default to undefined)
let approvalRequest: ApprovalRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.approveExecutionApiV1WorkflowsExecutionsExecutionIdApprovePost_0(
    executionId,
    approvalRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **approvalRequest** | **ApprovalRequest**|  | |
| **executionId** | [**string**] |  | defaults to undefined|
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

# **cancelExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdCancelPost**
> any cancelExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdCancelPost()

Cancel a running execution.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let executionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdCancelPost(
    workflowId,
    executionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **executionId** | [**string**] |  | defaults to undefined|
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

# **cancelExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdCancelPost_0**
> any cancelExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdCancelPost_0()

Cancel a running execution.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let executionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdCancelPost_0(
    workflowId,
    executionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **executionId** | [**string**] |  | defaults to undefined|
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

# **configureTriggerApiV1WorkflowsWorkflowIdTriggerPost**
> WorkflowResponse configureTriggerApiV1WorkflowsWorkflowIdTriggerPost(configureTriggerRequest)

Configure a workflow trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    ConfigureTriggerRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let configureTriggerRequest: ConfigureTriggerRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.configureTriggerApiV1WorkflowsWorkflowIdTriggerPost(
    workflowId,
    configureTriggerRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **configureTriggerRequest** | **ConfigureTriggerRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **configureTriggerApiV1WorkflowsWorkflowIdTriggerPost_0**
> WorkflowResponse configureTriggerApiV1WorkflowsWorkflowIdTriggerPost_0(configureTriggerRequest)

Configure a workflow trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    ConfigureTriggerRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let configureTriggerRequest: ConfigureTriggerRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.configureTriggerApiV1WorkflowsWorkflowIdTriggerPost_0(
    workflowId,
    configureTriggerRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **configureTriggerRequest** | **ConfigureTriggerRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **createWebhookApiV1WorkflowsWorkflowIdWebhooksPost**
> any createWebhookApiV1WorkflowsWorkflowIdWebhooksPost(createWebhookRequest)

Create a webhook for a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    CreateWebhookRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let createWebhookRequest: CreateWebhookRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createWebhookApiV1WorkflowsWorkflowIdWebhooksPost(
    workflowId,
    createWebhookRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createWebhookRequest** | **CreateWebhookRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **createWebhookApiV1WorkflowsWorkflowIdWebhooksPost_0**
> any createWebhookApiV1WorkflowsWorkflowIdWebhooksPost_0(createWebhookRequest)

Create a webhook for a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    CreateWebhookRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let createWebhookRequest: CreateWebhookRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createWebhookApiV1WorkflowsWorkflowIdWebhooksPost_0(
    workflowId,
    createWebhookRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createWebhookRequest** | **CreateWebhookRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **createWorkflowApiV1WorkflowsPost**
> WorkflowResponse createWorkflowApiV1WorkflowsPost(createWorkflowRequest)

Create a new workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    CreateWorkflowRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let createWorkflowRequest: CreateWorkflowRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createWorkflowApiV1WorkflowsPost(
    createWorkflowRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createWorkflowRequest** | **CreateWorkflowRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **createWorkflowApiV1WorkflowsPost_0**
> WorkflowResponse createWorkflowApiV1WorkflowsPost_0(createWorkflowRequest)

Create a new workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    CreateWorkflowRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let createWorkflowRequest: CreateWorkflowRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createWorkflowApiV1WorkflowsPost_0(
    createWorkflowRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createWorkflowRequest** | **CreateWorkflowRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **createWorkflowFromTemplateApiV1WorkflowsTemplatesTemplateIdCreatePost**
> WorkflowResponse createWorkflowFromTemplateApiV1WorkflowsTemplatesTemplateIdCreatePost(backendAppApiRoutesWorkflowsCreateFromTemplateRequest)

Create workflow from template.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    BackendAppApiRoutesWorkflowsCreateFromTemplateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let templateId: string; // (default to undefined)
let backendAppApiRoutesWorkflowsCreateFromTemplateRequest: BackendAppApiRoutesWorkflowsCreateFromTemplateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createWorkflowFromTemplateApiV1WorkflowsTemplatesTemplateIdCreatePost(
    templateId,
    backendAppApiRoutesWorkflowsCreateFromTemplateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesWorkflowsCreateFromTemplateRequest** | **BackendAppApiRoutesWorkflowsCreateFromTemplateRequest**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **createWorkflowFromTemplateApiV1WorkflowsTemplatesTemplateIdCreatePost_0**
> WorkflowResponse createWorkflowFromTemplateApiV1WorkflowsTemplatesTemplateIdCreatePost_0(backendAppApiRoutesWorkflowsCreateFromTemplateRequest)

Create workflow from template.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    BackendAppApiRoutesWorkflowsCreateFromTemplateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let templateId: string; // (default to undefined)
let backendAppApiRoutesWorkflowsCreateFromTemplateRequest: BackendAppApiRoutesWorkflowsCreateFromTemplateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createWorkflowFromTemplateApiV1WorkflowsTemplatesTemplateIdCreatePost_0(
    templateId,
    backendAppApiRoutesWorkflowsCreateFromTemplateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppApiRoutesWorkflowsCreateFromTemplateRequest** | **BackendAppApiRoutesWorkflowsCreateFromTemplateRequest**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **debugWorkflowApiV1WorkflowsWorkflowIdDebugPost**
> any debugWorkflowApiV1WorkflowsWorkflowIdDebugPost(debugWorkflowRequest)

Debug a workflow (dry run).

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    DebugWorkflowRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let debugWorkflowRequest: DebugWorkflowRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.debugWorkflowApiV1WorkflowsWorkflowIdDebugPost(
    workflowId,
    debugWorkflowRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **debugWorkflowRequest** | **DebugWorkflowRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **debugWorkflowApiV1WorkflowsWorkflowIdDebugPost_0**
> any debugWorkflowApiV1WorkflowsWorkflowIdDebugPost_0(debugWorkflowRequest)

Debug a workflow (dry run).

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    DebugWorkflowRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let debugWorkflowRequest: DebugWorkflowRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.debugWorkflowApiV1WorkflowsWorkflowIdDebugPost_0(
    workflowId,
    debugWorkflowRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **debugWorkflowRequest** | **DebugWorkflowRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **deleteTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDelete**
> any deleteTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDelete()

Delete a trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let triggerId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDelete(
    workflowId,
    triggerId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **triggerId** | [**string**] |  | defaults to undefined|
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

# **deleteTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDelete_0**
> any deleteTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDelete_0()

Delete a trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let triggerId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDelete_0(
    workflowId,
    triggerId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **triggerId** | [**string**] |  | defaults to undefined|
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

# **deleteWebhookApiV1WorkflowsWorkflowIdWebhooksWebhookIdDelete**
> any deleteWebhookApiV1WorkflowsWorkflowIdWebhooksWebhookIdDelete()

Delete a webhook.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let webhookId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteWebhookApiV1WorkflowsWorkflowIdWebhooksWebhookIdDelete(
    workflowId,
    webhookId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **webhookId** | [**string**] |  | defaults to undefined|
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

# **deleteWebhookApiV1WorkflowsWorkflowIdWebhooksWebhookIdDelete_0**
> any deleteWebhookApiV1WorkflowsWorkflowIdWebhooksWebhookIdDelete_0()

Delete a webhook.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let webhookId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteWebhookApiV1WorkflowsWorkflowIdWebhooksWebhookIdDelete_0(
    workflowId,
    webhookId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **webhookId** | [**string**] |  | defaults to undefined|
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

# **deleteWorkflowApiV1WorkflowsWorkflowIdDelete**
> any deleteWorkflowApiV1WorkflowsWorkflowIdDelete()

Delete a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteWorkflowApiV1WorkflowsWorkflowIdDelete(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **deleteWorkflowApiV1WorkflowsWorkflowIdDelete_0**
> any deleteWorkflowApiV1WorkflowsWorkflowIdDelete_0()

Delete a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteWorkflowApiV1WorkflowsWorkflowIdDelete_0(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **disableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDisablePost**
> any disableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDisablePost()

Disable a trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let triggerId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.disableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDisablePost(
    workflowId,
    triggerId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **triggerId** | [**string**] |  | defaults to undefined|
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

# **disableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDisablePost_0**
> any disableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDisablePost_0()

Disable a trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let triggerId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.disableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdDisablePost_0(
    workflowId,
    triggerId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **triggerId** | [**string**] |  | defaults to undefined|
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

# **enableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdEnablePost**
> any enableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdEnablePost()

Enable a trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let triggerId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.enableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdEnablePost(
    workflowId,
    triggerId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **triggerId** | [**string**] |  | defaults to undefined|
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

# **enableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdEnablePost_0**
> any enableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdEnablePost_0()

Enable a trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let triggerId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.enableTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdEnablePost_0(
    workflowId,
    triggerId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **triggerId** | [**string**] |  | defaults to undefined|
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

# **executeWorkflowApiV1WorkflowsWorkflowIdExecutePost**
> WorkflowExecutionResponse executeWorkflowApiV1WorkflowsWorkflowIdExecutePost(executeWorkflowRequest)

Execute a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    ExecuteWorkflowRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let executeWorkflowRequest: ExecuteWorkflowRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.executeWorkflowApiV1WorkflowsWorkflowIdExecutePost(
    workflowId,
    executeWorkflowRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **executeWorkflowRequest** | **ExecuteWorkflowRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowExecutionResponse**

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

# **executeWorkflowApiV1WorkflowsWorkflowIdExecutePost_0**
> WorkflowExecutionResponse executeWorkflowApiV1WorkflowsWorkflowIdExecutePost_0(executeWorkflowRequest)

Execute a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    ExecuteWorkflowRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let executeWorkflowRequest: ExecuteWorkflowRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.executeWorkflowApiV1WorkflowsWorkflowIdExecutePost_0(
    workflowId,
    executeWorkflowRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **executeWorkflowRequest** | **ExecuteWorkflowRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowExecutionResponse**

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

# **getExecutionApiV1WorkflowsExecutionsExecutionIdGet**
> WorkflowExecutionResponse getExecutionApiV1WorkflowsExecutionsExecutionIdGet()

Get execution status.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let executionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExecutionApiV1WorkflowsExecutionsExecutionIdGet(
    executionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **executionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowExecutionResponse**

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

# **getExecutionApiV1WorkflowsExecutionsExecutionIdGet_0**
> WorkflowExecutionResponse getExecutionApiV1WorkflowsExecutionsExecutionIdGet_0()

Get execution status.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let executionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExecutionApiV1WorkflowsExecutionsExecutionIdGet_0(
    executionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **executionId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowExecutionResponse**

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

# **getExecutionLogsApiV1WorkflowsWorkflowIdExecutionsExecutionIdLogsGet**
> any getExecutionLogsApiV1WorkflowsWorkflowIdExecutionsExecutionIdLogsGet()

Get execution logs.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let executionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExecutionLogsApiV1WorkflowsWorkflowIdExecutionsExecutionIdLogsGet(
    workflowId,
    executionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **executionId** | [**string**] |  | defaults to undefined|
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

# **getExecutionLogsApiV1WorkflowsWorkflowIdExecutionsExecutionIdLogsGet_0**
> any getExecutionLogsApiV1WorkflowsWorkflowIdExecutionsExecutionIdLogsGet_0()

Get execution logs.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let executionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExecutionLogsApiV1WorkflowsWorkflowIdExecutionsExecutionIdLogsGet_0(
    workflowId,
    executionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **executionId** | [**string**] |  | defaults to undefined|
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

# **getNodeTypeSchemaApiV1WorkflowsNodeTypesNodeTypeSchemaGet**
> any getNodeTypeSchemaApiV1WorkflowsNodeTypesNodeTypeSchemaGet()

Get schema for a node type.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let nodeType: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getNodeTypeSchemaApiV1WorkflowsNodeTypesNodeTypeSchemaGet(
    nodeType,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **nodeType** | [**string**] |  | defaults to undefined|
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

# **getNodeTypeSchemaApiV1WorkflowsNodeTypesNodeTypeSchemaGet_0**
> any getNodeTypeSchemaApiV1WorkflowsNodeTypesNodeTypeSchemaGet_0()

Get schema for a node type.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let nodeType: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getNodeTypeSchemaApiV1WorkflowsNodeTypesNodeTypeSchemaGet_0(
    nodeType,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **nodeType** | [**string**] |  | defaults to undefined|
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

# **getPendingApprovalsApiV1WorkflowsApprovalsPendingGet**
> any getPendingApprovalsApiV1WorkflowsApprovalsPendingGet()

Get all pending approvals.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPendingApprovalsApiV1WorkflowsApprovalsPendingGet(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | (optional) defaults to undefined|
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

# **getPendingApprovalsApiV1WorkflowsApprovalsPendingGet_0**
> any getPendingApprovalsApiV1WorkflowsApprovalsPendingGet_0()

Get all pending approvals.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPendingApprovalsApiV1WorkflowsApprovalsPendingGet_0(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | (optional) defaults to undefined|
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

# **getWorkflowApiV1WorkflowsWorkflowIdGet**
> WorkflowResponse getWorkflowApiV1WorkflowsWorkflowIdGet()

Get a workflow by ID.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWorkflowApiV1WorkflowsWorkflowIdGet(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **getWorkflowApiV1WorkflowsWorkflowIdGet_0**
> WorkflowResponse getWorkflowApiV1WorkflowsWorkflowIdGet_0()

Get a workflow by ID.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWorkflowApiV1WorkflowsWorkflowIdGet_0(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet**
> Array<WorkflowExecutionResponse> listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet()

List executions for a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let status: ExecutionStatus; // (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet(
    workflowId,
    status,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **status** | **ExecutionStatus** |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<WorkflowExecutionResponse>**

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

# **listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet_0**
> Array<WorkflowExecutionResponse> listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet_0()

List executions for a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let status: ExecutionStatus; // (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet_0(
    workflowId,
    status,
    limit,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **status** | **ExecutionStatus** |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<WorkflowExecutionResponse>**

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

# **listNodeTypesApiV1WorkflowsNodeTypesGet**
> any listNodeTypesApiV1WorkflowsNodeTypesGet()

List available node types.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listNodeTypesApiV1WorkflowsNodeTypesGet(
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

# **listNodeTypesApiV1WorkflowsNodeTypesGet_0**
> any listNodeTypesApiV1WorkflowsNodeTypesGet_0()

List available node types.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listNodeTypesApiV1WorkflowsNodeTypesGet_0(
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

# **listWebhooksApiV1WorkflowsWorkflowIdWebhooksGet**
> any listWebhooksApiV1WorkflowsWorkflowIdWebhooksGet()

List webhooks for a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWebhooksApiV1WorkflowsWorkflowIdWebhooksGet(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **listWebhooksApiV1WorkflowsWorkflowIdWebhooksGet_0**
> any listWebhooksApiV1WorkflowsWorkflowIdWebhooksGet_0()

List webhooks for a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWebhooksApiV1WorkflowsWorkflowIdWebhooksGet_0(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **listWorkflowTemplatesApiV1WorkflowsTemplatesGet**
> any listWorkflowTemplatesApiV1WorkflowsTemplatesGet()

List workflow templates.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWorkflowTemplatesApiV1WorkflowsTemplatesGet(
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

# **listWorkflowTemplatesApiV1WorkflowsTemplatesGet_0**
> any listWorkflowTemplatesApiV1WorkflowsTemplatesGet_0()

List workflow templates.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWorkflowTemplatesApiV1WorkflowsTemplatesGet_0(
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

# **listWorkflowsApiV1WorkflowsGet**
> WorkflowListResponse listWorkflowsApiV1WorkflowsGet()

List all workflows.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let activeOnly: boolean; //Only return active workflows (optional) (default to false)
let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWorkflowsApiV1WorkflowsGet(
    activeOnly,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **activeOnly** | [**boolean**] | Only return active workflows | (optional) defaults to false|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowListResponse**

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

# **listWorkflowsApiV1WorkflowsGet_0**
> WorkflowListResponse listWorkflowsApiV1WorkflowsGet_0()

List all workflows.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let activeOnly: boolean; //Only return active workflows (optional) (default to false)
let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWorkflowsApiV1WorkflowsGet_0(
    activeOnly,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **activeOnly** | [**boolean**] | Only return active workflows | (optional) defaults to false|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowListResponse**

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

# **regenerateWebhookSecretApiV1WorkflowsWorkflowIdWebhooksWebhookIdRegenerateSecretPost**
> any regenerateWebhookSecretApiV1WorkflowsWorkflowIdWebhooksWebhookIdRegenerateSecretPost()

Regenerate webhook secret.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let webhookId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.regenerateWebhookSecretApiV1WorkflowsWorkflowIdWebhooksWebhookIdRegenerateSecretPost(
    workflowId,
    webhookId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **webhookId** | [**string**] |  | defaults to undefined|
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

# **regenerateWebhookSecretApiV1WorkflowsWorkflowIdWebhooksWebhookIdRegenerateSecretPost_0**
> any regenerateWebhookSecretApiV1WorkflowsWorkflowIdWebhooksWebhookIdRegenerateSecretPost_0()

Regenerate webhook secret.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let webhookId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.regenerateWebhookSecretApiV1WorkflowsWorkflowIdWebhooksWebhookIdRegenerateSecretPost_0(
    workflowId,
    webhookId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **webhookId** | [**string**] |  | defaults to undefined|
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

# **retryExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdRetryPost**
> any retryExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdRetryPost()

Retry a failed execution.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let executionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.retryExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdRetryPost(
    workflowId,
    executionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **executionId** | [**string**] |  | defaults to undefined|
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

# **retryExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdRetryPost_0**
> any retryExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdRetryPost_0()

Retry a failed execution.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let executionId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.retryExecutionApiV1WorkflowsWorkflowIdExecutionsExecutionIdRetryPost_0(
    workflowId,
    executionId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
| **executionId** | [**string**] |  | defaults to undefined|
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

# **saveAsTemplateApiV1WorkflowsWorkflowIdSaveAsTemplatePost**
> any saveAsTemplateApiV1WorkflowsWorkflowIdSaveAsTemplatePost()

Save workflow as a reusable template.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.saveAsTemplateApiV1WorkflowsWorkflowIdSaveAsTemplatePost(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **saveAsTemplateApiV1WorkflowsWorkflowIdSaveAsTemplatePost_0**
> any saveAsTemplateApiV1WorkflowsWorkflowIdSaveAsTemplatePost_0()

Save workflow as a reusable template.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.saveAsTemplateApiV1WorkflowsWorkflowIdSaveAsTemplatePost_0(
    workflowId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **workflowId** | [**string**] |  | defaults to undefined|
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

# **updateTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdPut**
> any updateTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdPut(configureTriggerRequest)

Update a specific trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    ConfigureTriggerRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let triggerId: string; // (default to undefined)
let configureTriggerRequest: ConfigureTriggerRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdPut(
    workflowId,
    triggerId,
    configureTriggerRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **configureTriggerRequest** | **ConfigureTriggerRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
| **triggerId** | [**string**] |  | defaults to undefined|
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

# **updateTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdPut_0**
> any updateTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdPut_0(configureTriggerRequest)

Update a specific trigger.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    ConfigureTriggerRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let triggerId: string; // (default to undefined)
let configureTriggerRequest: ConfigureTriggerRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTriggerApiV1WorkflowsWorkflowIdTriggersTriggerIdPut_0(
    workflowId,
    triggerId,
    configureTriggerRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **configureTriggerRequest** | **ConfigureTriggerRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
| **triggerId** | [**string**] |  | defaults to undefined|
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

# **updateWorkflowApiV1WorkflowsWorkflowIdPut**
> WorkflowResponse updateWorkflowApiV1WorkflowsWorkflowIdPut(updateWorkflowRequest)

Update a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    UpdateWorkflowRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let updateWorkflowRequest: UpdateWorkflowRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateWorkflowApiV1WorkflowsWorkflowIdPut(
    workflowId,
    updateWorkflowRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateWorkflowRequest** | **UpdateWorkflowRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

# **updateWorkflowApiV1WorkflowsWorkflowIdPut_0**
> WorkflowResponse updateWorkflowApiV1WorkflowsWorkflowIdPut_0(updateWorkflowRequest)

Update a workflow.

### Example

```typescript
import {
    WorkflowsApi,
    Configuration,
    UpdateWorkflowRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new WorkflowsApi(configuration);

let workflowId: string; // (default to undefined)
let updateWorkflowRequest: UpdateWorkflowRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateWorkflowApiV1WorkflowsWorkflowIdPut_0(
    workflowId,
    updateWorkflowRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateWorkflowRequest** | **UpdateWorkflowRequest**|  | |
| **workflowId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WorkflowResponse**

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

