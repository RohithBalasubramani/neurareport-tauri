# TaskEventResponse

Task event for audit trail.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **string** |  | [optional] [default to undefined]
**event_data** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**event_type** | **string** |  | [default to undefined]
**id** | **number** |  | [default to undefined]
**new_status** | **string** |  | [optional] [default to undefined]
**previous_status** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TaskEventResponse } from './api';

const instance: TaskEventResponse = {
    created_at,
    event_data,
    event_type,
    id,
    new_status,
    previous_status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
