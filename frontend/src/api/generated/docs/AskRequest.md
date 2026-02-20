# AskRequest

Request to ask a question.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**include_citations** | **boolean** |  | [optional] [default to true]
**max_response_length** | **number** |  | [optional] [default to 2000]
**question** | **string** |  | [default to undefined]

## Example

```typescript
import { AskRequest } from './api';

const instance: AskRequest = {
    include_citations,
    max_response_length,
    question,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
