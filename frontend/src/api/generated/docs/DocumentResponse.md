# DocumentResponse

Document response model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**collaboration_enabled** | **boolean** |  | [default to undefined]
**content** | [**DocumentContent**](DocumentContent.md) |  | [default to undefined]
**content_type** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**is_template** | **boolean** |  | [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**owner_id** | **string** |  | [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [default to undefined]
**track_changes_enabled** | **boolean** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**version** | **number** |  | [default to undefined]

## Example

```typescript
import { DocumentResponse } from './api';

const instance: DocumentResponse = {
    collaboration_enabled,
    content,
    content_type,
    created_at,
    id,
    is_template,
    metadata,
    name,
    owner_id,
    tags,
    track_changes_enabled,
    updated_at,
    version,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
