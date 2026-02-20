# WorkflowExecutionResponse

Workflow execution status response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **string** |  | [optional] [default to undefined]
**finished_at** | **string** |  | [optional] [default to undefined]
**id** | **string** |  | [default to undefined]
**input_data** | **{ [key: string]: any; }** |  | [default to undefined]
**node_results** | [**Array&lt;NodeExecutionResult&gt;**](NodeExecutionResult.md) |  | [optional] [default to undefined]
**output_data** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**started_at** | **string** |  | [default to undefined]
**status** | [**ExecutionStatus**](ExecutionStatus.md) |  | [default to undefined]
**workflow_id** | **string** |  | [default to undefined]

## Example

```typescript
import { WorkflowExecutionResponse } from './api';

const instance: WorkflowExecutionResponse = {
    error,
    finished_at,
    id,
    input_data,
    node_results,
    output_data,
    started_at,
    status,
    workflow_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
