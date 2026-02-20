# NodeExecutionResult

Result of executing a single node.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **string** |  | [optional] [default to undefined]
**finished_at** | **string** |  | [optional] [default to undefined]
**node_id** | **string** |  | [default to undefined]
**output** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**started_at** | **string** |  | [default to undefined]
**status** | [**ExecutionStatus**](ExecutionStatus.md) |  | [default to undefined]

## Example

```typescript
import { NodeExecutionResult } from './api';

const instance: NodeExecutionResult = {
    error,
    finished_at,
    node_id,
    output,
    started_at,
    status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
