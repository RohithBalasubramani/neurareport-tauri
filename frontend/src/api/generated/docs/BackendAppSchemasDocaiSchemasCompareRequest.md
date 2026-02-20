# BackendAppSchemasDocaiSchemasCompareRequest

Request to compare documents.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_a_content** | **string** |  | [optional] [default to undefined]
**document_a_path** | **string** |  | [optional] [default to undefined]
**document_b_content** | **string** |  | [optional] [default to undefined]
**document_b_path** | **string** |  | [optional] [default to undefined]
**highlight_changes** | **boolean** |  | [optional] [default to true]
**semantic_comparison** | **boolean** |  | [optional] [default to false]

## Example

```typescript
import { BackendAppSchemasDocaiSchemasCompareRequest } from './api';

const instance: BackendAppSchemasDocaiSchemasCompareRequest = {
    document_a_content,
    document_a_path,
    document_b_content,
    document_b_path,
    highlight_changes,
    semantic_comparison,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
