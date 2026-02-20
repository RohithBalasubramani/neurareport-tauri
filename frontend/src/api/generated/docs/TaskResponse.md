# TaskResponse

Standard task response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agent_type** | **string** |  | [default to undefined]
**attempts** | [**AttemptsResponse**](AttemptsResponse.md) |  | [default to undefined]
**cost** | [**CostResponse**](CostResponse.md) |  | [default to undefined]
**error** | [**ErrorResponse**](ErrorResponse.md) |  | [optional] [default to undefined]
**links** | [**LinksResponse**](LinksResponse.md) |  | [default to undefined]
**progress** | [**ProgressResponse**](ProgressResponse.md) |  | [default to undefined]
**result** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**status** | **string** |  | [default to undefined]
**task_id** | **string** |  | [default to undefined]
**timestamps** | [**TimestampsResponse**](TimestampsResponse.md) |  | [default to undefined]

## Example

```typescript
import { TaskResponse } from './api';

const instance: TaskResponse = {
    agent_type,
    attempts,
    cost,
    error,
    links,
    progress,
    result,
    status,
    task_id,
    timestamps,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
