# BackendAppApiRoutesAgentsV2EmailDraftRequest

Request to run the email draft agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | **string** | Background context for the email | [default to undefined]
**idempotency_key** | **string** |  | [optional] [default to undefined]
**include_subject** | **boolean** |  | [optional] [default to true]
**previous_emails** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**priority** | **number** |  | [optional] [default to 0]
**purpose** | **string** | Purpose/intent of the email | [default to undefined]
**recipient_info** | **string** |  | [optional] [default to undefined]
**sync** | **boolean** |  | [optional] [default to true]
**tone** | **string** | Tone: professional, friendly, formal, casual, empathetic, assertive | [optional] [default to 'professional']
**webhook_url** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { BackendAppApiRoutesAgentsV2EmailDraftRequest } from './api';

const instance: BackendAppApiRoutesAgentsV2EmailDraftRequest = {
    context,
    idempotency_key,
    include_subject,
    previous_emails,
    priority,
    purpose,
    recipient_info,
    sync,
    tone,
    webhook_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
