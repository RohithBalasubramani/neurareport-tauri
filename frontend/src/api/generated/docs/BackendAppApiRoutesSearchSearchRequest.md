# BackendAppApiRoutesSearchSearchRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**facet_fields** | **Array&lt;string&gt;** | Facet fields | [optional] [default to undefined]
**filters** | **Array&lt;{ [key: string]: any; }&gt;** | Filters | [optional] [default to undefined]
**highlight** | **boolean** | Highlight matches | [optional] [default to true]
**page** | **number** | Page number | [optional] [default to 1]
**page_size** | **number** | Results per page | [optional] [default to 20]
**query** | **string** | Search query | [default to undefined]
**search_type** | **string** | Search type | [optional] [default to 'fulltext']
**typo_tolerance** | **boolean** | Enable typo tolerance | [optional] [default to true]

## Example

```typescript
import { BackendAppApiRoutesSearchSearchRequest } from './api';

const instance: BackendAppApiRoutesSearchSearchRequest = {
    facet_fields,
    filters,
    highlight,
    page,
    page_size,
    query,
    search_type,
    typo_tolerance,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
