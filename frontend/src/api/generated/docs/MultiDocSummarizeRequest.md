# MultiDocSummarizeRequest

Request to summarize multiple documents.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_ids** | **Array&lt;string&gt;** |  | [default to undefined]
**focus_topics** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**include_sources** | **boolean** |  | [optional] [default to true]
**max_length** | **number** |  | [optional] [default to 500]

## Example

```typescript
import { MultiDocSummarizeRequest } from './api';

const instance: MultiDocSummarizeRequest = {
    document_ids,
    focus_topics,
    include_sources,
    max_length,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
