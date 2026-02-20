# ShareRequest

Request model for creating share links.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_level** | **string** |  | [optional] [default to 'view']
**allowed_emails** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**expires_hours** | **number** |  | [optional] [default to undefined]
**password_protected** | **boolean** |  | [optional] [default to false]

## Example

```typescript
import { ShareRequest } from './api';

const instance: ShareRequest = {
    access_level,
    allowed_emails,
    expires_hours,
    password_protected,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
