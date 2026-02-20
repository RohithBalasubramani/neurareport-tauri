# CreateDocumentRequest

Request to create a new document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**DocumentContent**](DocumentContent.md) |  | [optional] [default to undefined]
**is_template** | **boolean** |  | [optional] [default to false]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**tags** | **Array&lt;string | null&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { CreateDocumentRequest } from './api';

const instance: CreateDocumentRequest = {
    content,
    is_template,
    metadata,
    name,
    tags,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
