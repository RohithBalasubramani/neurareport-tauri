# QueryResponse

Query response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**columns** | **Array&lt;string&gt;** |  | [default to undefined]
**error** | **string** |  | [default to undefined]
**execution_time_ms** | **number** |  | [default to undefined]
**row_count** | **number** |  | [default to undefined]
**rows** | **Array&lt;Array&lt;any&gt;&gt;** |  | [default to undefined]
**truncated** | **boolean** |  | [default to undefined]

## Example

```typescript
import { QueryResponse } from './api';

const instance: QueryResponse = {
    columns,
    error,
    execution_time_ms,
    row_count,
    rows,
    truncated,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
