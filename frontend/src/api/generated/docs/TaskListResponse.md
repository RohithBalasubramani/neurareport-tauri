# TaskListResponse

Response for task listing.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**limit** | **number** |  | [default to undefined]
**offset** | **number** |  | [default to undefined]
**tasks** | [**Array&lt;TaskResponse&gt;**](TaskResponse.md) |  | [default to undefined]
**total** | **number** |  | [default to undefined]

## Example

```typescript
import { TaskListResponse } from './api';

const instance: TaskListResponse = {
    limit,
    offset,
    tasks,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
