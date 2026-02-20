# FederatedQueryRequest

Request to execute a federated query.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**limit** | **number** |  | [optional] [default to 100]
**sql** | **string** |  | [default to undefined]
**virtual_schema_id** | **string** |  | [default to undefined]

## Example

```typescript
import { FederatedQueryRequest } from './api';

const instance: FederatedQueryRequest = {
    limit,
    sql,
    virtual_schema_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
