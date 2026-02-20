# LibraryDocumentCreate

Request to add a document to the library.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**collections** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**document_type** | [**BackendAppSchemasKnowledgeLibraryDocumentType**](BackendAppSchemasKnowledgeLibraryDocumentType.md) |  | [optional] [default to undefined]
**file_path** | **string** |  | [optional] [default to undefined]
**file_url** | **string** |  | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**title** | **string** |  | [default to undefined]

## Example

```typescript
import { LibraryDocumentCreate } from './api';

const instance: LibraryDocumentCreate = {
    collections,
    description,
    document_type,
    file_path,
    file_url,
    metadata,
    tags,
    title,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
