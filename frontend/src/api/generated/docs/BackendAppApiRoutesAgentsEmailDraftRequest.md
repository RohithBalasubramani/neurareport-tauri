# BackendAppApiRoutesAgentsEmailDraftRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | **string** | Email context | [default to undefined]
**previous_emails** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**purpose** | **string** | Email purpose | [default to undefined]
**recipient_info** | **string** |  | [optional] [default to undefined]
**tone** | **string** | Email tone | [optional] [default to 'professional']

## Example

```typescript
import { BackendAppApiRoutesAgentsEmailDraftRequest } from './api';

const instance: BackendAppApiRoutesAgentsEmailDraftRequest = {
    context,
    previous_emails,
    purpose,
    recipient_info,
    tone,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
