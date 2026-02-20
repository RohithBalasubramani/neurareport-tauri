# ProgressResponse

Progress information for a task.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**current_step** | **string** |  | [optional] [default to undefined]
**current_step_num** | **number** |  | [optional] [default to undefined]
**message** | **string** |  | [optional] [default to undefined]
**percent** | **number** |  | [default to undefined]
**total_steps** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { ProgressResponse } from './api';

const instance: ProgressResponse = {
    current_step,
    current_step_num,
    message,
    percent,
    total_steps,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
