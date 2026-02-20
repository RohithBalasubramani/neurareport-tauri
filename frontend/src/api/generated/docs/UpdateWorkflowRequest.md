# UpdateWorkflowRequest

Request to update a workflow.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **string** |  | [optional] [default to undefined]
**edges** | [**Array&lt;WorkflowEdge&gt;**](WorkflowEdge.md) |  | [optional] [default to undefined]
**is_active** | **boolean** |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**nodes** | [**Array&lt;WorkflowNode&gt;**](WorkflowNode.md) |  | [optional] [default to undefined]
**triggers** | [**Array&lt;WorkflowTrigger&gt;**](WorkflowTrigger.md) |  | [optional] [default to undefined]

## Example

```typescript
import { UpdateWorkflowRequest } from './api';

const instance: UpdateWorkflowRequest = {
    description,
    edges,
    is_active,
    name,
    nodes,
    triggers,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
