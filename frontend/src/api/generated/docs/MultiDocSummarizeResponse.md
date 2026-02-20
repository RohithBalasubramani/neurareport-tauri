# MultiDocSummarizeResponse

Multi-document summary result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**common_themes** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**document_count** | **number** |  | [default to undefined]
**key_points** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**sources** | [**Array&lt;SummarySource&gt;**](SummarySource.md) |  | [optional] [default to undefined]
**summary** | **string** |  | [default to undefined]

## Example

```typescript
import { MultiDocSummarizeResponse } from './api';

const instance: MultiDocSummarizeResponse = {
    common_themes,
    document_count,
    key_points,
    processing_time_ms,
    sources,
    summary,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
