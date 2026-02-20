# BackendAppApiRoutesAgentsV2ContentRepurposeRequest

Request to run the content repurposing agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**adapt_length** | **boolean** |  | [optional] [default to true]
**content** | **string** | Source content to repurpose | [default to undefined]
**idempotency_key** | **string** |  | [optional] [default to undefined]
**preserve_key_points** | **boolean** |  | [optional] [default to true]
**priority** | **number** |  | [optional] [default to 0]
**source_format** | **string** | Format of the source content (article, report, transcript, etc.) | [default to undefined]
**sync** | **boolean** |  | [optional] [default to true]
**target_formats** | **Array&lt;string&gt;** | Target formats: tweet_thread, linkedin_post, blog_summary, slides, email_newsletter, video_script, infographic, podcast_notes, press_release, executive_summary | [default to undefined]
**webhook_url** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { BackendAppApiRoutesAgentsV2ContentRepurposeRequest } from './api';

const instance: BackendAppApiRoutesAgentsV2ContentRepurposeRequest = {
    adapt_length,
    content,
    idempotency_key,
    preserve_key_points,
    priority,
    source_format,
    sync,
    target_formats,
    webhook_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
