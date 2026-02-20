# FAQGenerateRequest

Request to generate FAQ from documents.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**categories** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**document_ids** | **Array&lt;string&gt;** |  | [default to undefined]
**max_questions** | **number** |  | [optional] [default to 10]

## Example

```typescript
import { FAQGenerateRequest } from './api';

const instance: FAQGenerateRequest = {
    categories,
    document_ids,
    max_questions,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
