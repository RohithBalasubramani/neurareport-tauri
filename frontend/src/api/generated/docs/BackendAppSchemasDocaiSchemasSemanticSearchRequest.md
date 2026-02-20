# BackendAppSchemasDocaiSchemasSemanticSearchRequest

Request for semantic search.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**query** | **string** |  | [default to undefined]
**threshold** | **number** |  | [optional] [default to 0.5]
**top_k** | **number** |  | [optional] [default to 10]

## Example

```typescript
import { BackendAppSchemasDocaiSchemasSemanticSearchRequest } from './api';

const instance: BackendAppSchemasDocaiSchemasSemanticSearchRequest = {
    document_ids,
    query,
    threshold,
    top_k,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
