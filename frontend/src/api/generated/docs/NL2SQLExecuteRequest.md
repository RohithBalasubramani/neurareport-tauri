# NL2SQLExecuteRequest

Request to execute a SQL query.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection_id** | **string** |  | [default to undefined]
**include_total** | **boolean** |  | [optional] [default to false]
**limit** | **number** |  | [optional] [default to 100]
**offset** | **number** |  | [optional] [default to 0]
**sql** | **string** |  | [default to undefined]

## Example

```typescript
import { NL2SQLExecuteRequest } from './api';

const instance: NL2SQLExecuteRequest = {
    connection_id,
    include_total,
    limit,
    offset,
    sql,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
