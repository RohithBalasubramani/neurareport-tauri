# QuestionRequest

Request model for asking questions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**include_sources** | **boolean** |  | [optional] [default to true]
**max_context_chunks** | **number** |  | [optional] [default to 5]
**question** | **string** |  | [default to undefined]

## Example

```typescript
import { QuestionRequest } from './api';

const instance: QuestionRequest = {
    include_sources,
    max_context_chunks,
    question,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
