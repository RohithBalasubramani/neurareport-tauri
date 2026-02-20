# SearchReplaceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**dry_run** | **boolean** | Preview only | [optional] [default to true]
**replace_with** | **string** | Replacement text | [default to undefined]
**search_query** | **string** | Text to search | [default to undefined]

## Example

```typescript
import { SearchReplaceRequest } from './api';

const instance: SearchReplaceRequest = {
    document_ids,
    dry_run,
    replace_with,
    search_query,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
