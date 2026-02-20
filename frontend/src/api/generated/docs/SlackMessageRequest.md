# SlackMessageRequest

Request to send to Slack.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**channel** | **string** |  | [default to undefined]
**document_id** | **string** |  | [default to undefined]
**message** | **string** |  | [optional] [default to undefined]
**thread_ts** | **string** |  | [optional] [default to undefined]
**upload_file** | **boolean** |  | [optional] [default to true]

## Example

```typescript
import { SlackMessageRequest } from './api';

const instance: SlackMessageRequest = {
    channel,
    document_id,
    message,
    thread_ts,
    upload_file,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
