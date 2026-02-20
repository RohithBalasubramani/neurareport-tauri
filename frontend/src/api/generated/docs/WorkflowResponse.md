# WorkflowResponse

Workflow response model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **string** |  | [default to undefined]
**description** | **string** |  | [default to undefined]
**edges** | [**Array&lt;WorkflowEdge&gt;**](WorkflowEdge.md) |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**is_active** | **boolean** |  | [default to undefined]
**last_run_at** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**nodes** | [**Array&lt;WorkflowNode&gt;**](WorkflowNode.md) |  | [default to undefined]
**run_count** | **number** |  | [optional] [default to 0]
**triggers** | [**Array&lt;WorkflowTrigger&gt;**](WorkflowTrigger.md) |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]

## Example

```typescript
import { WorkflowResponse } from './api';

const instance: WorkflowResponse = {
    created_at,
    description,
    edges,
    id,
    is_active,
    last_run_at,
    name,
    nodes,
    run_count,
    triggers,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
