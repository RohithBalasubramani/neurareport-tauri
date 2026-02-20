# WorkflowNode

A single node in a workflow.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**id** | **string** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**position** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**type** | [**NodeType**](NodeType.md) |  | [default to undefined]

## Example

```typescript
import { WorkflowNode } from './api';

const instance: WorkflowNode = {
    config,
    id,
    name,
    position,
    type,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
