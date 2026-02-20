# NL2SQLSaveRequest

Request to save a query as a reusable data source.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection_id** | **string** |  | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**original_question** | **string** |  | [optional] [default to undefined]
**sql** | **string** |  | [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { NL2SQLSaveRequest } from './api';

const instance: NL2SQLSaveRequest = {
    connection_id,
    description,
    name,
    original_question,
    sql,
    tags,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
