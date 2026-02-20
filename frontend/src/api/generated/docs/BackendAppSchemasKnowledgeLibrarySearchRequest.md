# BackendAppSchemasKnowledgeLibrarySearchRequest

Search request model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**collections** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**date_from** | **string** |  | [optional] [default to undefined]
**date_to** | **string** |  | [optional] [default to undefined]
**document_types** | [**Array&lt;BackendAppSchemasKnowledgeLibraryDocumentType&gt;**](BackendAppSchemasKnowledgeLibraryDocumentType.md) |  | [optional] [default to undefined]
**limit** | **number** |  | [optional] [default to 50]
**offset** | **number** |  | [optional] [default to 0]
**query** | **string** |  | [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { BackendAppSchemasKnowledgeLibrarySearchRequest } from './api';

const instance: BackendAppSchemasKnowledgeLibrarySearchRequest = {
    collections,
    date_from,
    date_to,
    document_types,
    limit,
    offset,
    query,
    tags,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
