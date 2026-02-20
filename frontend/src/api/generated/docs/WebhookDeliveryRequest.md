# WebhookDeliveryRequest

Request to deliver via webhook.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **string** |  | [default to undefined]
**headers** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**include_content** | **boolean** |  | [optional] [default to true]
**method** | **string** |  | [optional] [default to 'POST']
**payload_template** | **string** |  | [optional] [default to undefined]
**webhook_url** | **string** |  | [default to undefined]

## Example

```typescript
import { WebhookDeliveryRequest } from './api';

const instance: WebhookDeliveryRequest = {
    document_id,
    headers,
    include_content,
    method,
    payload_template,
    webhook_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
