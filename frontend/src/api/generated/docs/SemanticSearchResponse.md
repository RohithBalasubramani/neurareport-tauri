# SemanticSearchResponse

Semantic search results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**processing_time_ms** | **number** |  | [default to undefined]
**query** | **string** |  | [default to undefined]
**results** | [**Array&lt;BackendAppSchemasDocaiSchemasSearchResult&gt;**](BackendAppSchemasDocaiSchemasSearchResult.md) |  | [optional] [default to undefined]
**total_results** | **number** |  | [default to undefined]

## Example

```typescript
import { SemanticSearchResponse } from './api';

const instance: SemanticSearchResponse = {
    processing_time_ms,
    query,
    results,
    total_results,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
