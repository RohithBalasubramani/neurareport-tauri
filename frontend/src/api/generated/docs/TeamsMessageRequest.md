# TeamsMessageRequest

Request to send to Microsoft Teams.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **string** |  | [default to undefined]
**mention_users** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**message** | **string** |  | [optional] [default to undefined]
**title** | **string** |  | [optional] [default to undefined]
**webhook_url** | **string** |  | [default to undefined]

## Example

```typescript
import { TeamsMessageRequest } from './api';

const instance: TeamsMessageRequest = {
    document_id,
    mention_users,
    message,
    title,
    webhook_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
