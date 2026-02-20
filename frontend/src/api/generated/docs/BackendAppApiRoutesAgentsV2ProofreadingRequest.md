# BackendAppApiRoutesAgentsV2ProofreadingRequest

Request to run the proofreading agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**focus_areas** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**idempotency_key** | **string** |  | [optional] [default to undefined]
**preserve_voice** | **boolean** | Preserve the author\&#39;s voice while correcting | [optional] [default to true]
**priority** | **number** |  | [optional] [default to 0]
**style_guide** | **string** |  | [optional] [default to undefined]
**sync** | **boolean** |  | [optional] [default to true]
**text** | **string** | Text to proofread | [default to undefined]
**webhook_url** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { BackendAppApiRoutesAgentsV2ProofreadingRequest } from './api';

const instance: BackendAppApiRoutesAgentsV2ProofreadingRequest = {
    focus_areas,
    idempotency_key,
    preserve_voice,
    priority,
    style_guide,
    sync,
    text,
    webhook_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
