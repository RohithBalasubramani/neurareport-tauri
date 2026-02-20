# PortalPublishRequest

Request to publish document to portal.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **string** |  | [optional] [default to undefined]
**document_id** | **string** |  | [default to undefined]
**expires_at** | **string** |  | [optional] [default to undefined]
**password** | **string** |  | [optional] [default to undefined]
**portal_path** | **string** |  | [default to undefined]
**_public** | **boolean** |  | [optional] [default to false]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**title** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { PortalPublishRequest } from './api';

const instance: PortalPublishRequest = {
    description,
    document_id,
    expires_at,
    password,
    portal_path,
    _public,
    tags,
    title,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
