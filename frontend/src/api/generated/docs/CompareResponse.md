# CompareResponse

Document comparison result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**differences** | [**Array&lt;DocumentDiff&gt;**](DocumentDiff.md) |  | [optional] [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**significant_changes** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**similarity_score** | **number** |  | [default to undefined]
**summary** | **string** |  | [default to undefined]

## Example

```typescript
import { CompareResponse } from './api';

const instance: CompareResponse = {
    differences,
    processing_time_ms,
    significant_changes,
    similarity_score,
    summary,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
