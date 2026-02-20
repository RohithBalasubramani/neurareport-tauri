# ErrorResponse

Error information for a failed task.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **string** |  | [optional] [default to undefined]
**message** | **string** |  | [optional] [default to undefined]
**retryable** | **boolean** |  | [optional] [default to true]

## Example

```typescript
import { ErrorResponse } from './api';

const instance: ErrorResponse = {
    code,
    message,
    retryable,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
