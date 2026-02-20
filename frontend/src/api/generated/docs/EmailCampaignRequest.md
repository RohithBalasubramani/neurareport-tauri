# EmailCampaignRequest

Request for bulk email distribution.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attach_documents** | **boolean** |  | [optional] [default to true]
**document_ids** | **Array&lt;string&gt;** |  | [default to undefined]
**from_name** | **string** |  | [optional] [default to undefined]
**message** | **string** |  | [default to undefined]
**recipients** | **Array&lt;string&gt;** |  | [default to undefined]
**reply_to** | **string** |  | [optional] [default to undefined]
**subject** | **string** |  | [default to undefined]
**track_opens** | **boolean** |  | [optional] [default to true]

## Example

```typescript
import { EmailCampaignRequest } from './api';

const instance: EmailCampaignRequest = {
    attach_documents,
    document_ids,
    from_name,
    message,
    recipients,
    reply_to,
    subject,
    track_opens,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
