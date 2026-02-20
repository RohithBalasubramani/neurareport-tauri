# ConnectionUpsertRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**database** | **string** |  | [optional] [default to undefined]
**db_type** | **string** |  | [optional] [default to 'sqlite']
**db_url** | **string** |  | [optional] [default to undefined]
**id** | **string** |  | [optional] [default to undefined]
**latency_ms** | **number** |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**status** | **string** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { ConnectionUpsertRequest } from './api';

const instance: ConnectionUpsertRequest = {
    database,
    db_type,
    db_url,
    id,
    latency_ms,
    name,
    status,
    tags,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
