# ClassifyResponse

Document classification result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**all_scores** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**category** | [**DocumentCategory**](DocumentCategory.md) |  | [default to undefined]
**confidence** | **number** |  | [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**suggested_parsers** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { ClassifyResponse } from './api';

const instance: ClassifyResponse = {
    all_scores,
    category,
    confidence,
    processing_time_ms,
    suggested_parsers,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
