# UpdateDocumentRequest

Request to update a document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**DocumentContent**](DocumentContent.md) |  | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**track_changes_enabled** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { UpdateDocumentRequest } from './api';

const instance: UpdateDocumentRequest = {
    content,
    metadata,
    name,
    tags,
    track_changes_enabled,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
