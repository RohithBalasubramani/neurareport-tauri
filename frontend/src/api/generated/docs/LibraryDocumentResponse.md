# LibraryDocumentResponse

Library document response model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**collections** | **Array&lt;string&gt;** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**description** | **string** |  | [default to undefined]
**document_type** | [**BackendAppSchemasKnowledgeLibraryDocumentType**](BackendAppSchemasKnowledgeLibraryDocumentType.md) |  | [default to undefined]
**file_path** | **string** |  | [default to undefined]
**file_size** | **number** |  | [default to undefined]
**file_url** | **string** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**is_favorite** | **boolean** |  | [optional] [default to false]
**last_accessed_at** | **string** |  | [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [default to undefined]
**title** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]

## Example

```typescript
import { LibraryDocumentResponse } from './api';

const instance: LibraryDocumentResponse = {
    collections,
    created_at,
    description,
    document_type,
    file_path,
    file_size,
    file_url,
    id,
    is_favorite,
    last_accessed_at,
    metadata,
    tags,
    title,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
