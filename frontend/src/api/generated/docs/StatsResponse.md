# StatsResponse

Service statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cancelled** | **number** |  | [optional] [default to 0]
**completed** | **number** |  | [optional] [default to 0]
**failed** | **number** |  | [optional] [default to 0]
**pending** | **number** |  | [optional] [default to 0]
**retrying** | **number** |  | [optional] [default to 0]
**running** | **number** |  | [optional] [default to 0]
**total** | **number** |  | [optional] [default to 0]

## Example

```typescript
import { StatsResponse } from './api';

const instance: StatsResponse = {
    cancelled,
    completed,
    failed,
    pending,
    retrying,
    running,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
