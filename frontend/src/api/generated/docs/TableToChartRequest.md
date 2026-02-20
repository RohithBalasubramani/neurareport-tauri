# TableToChartRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chart_type** | **string** | Chart type | [optional] [default to 'bar']
**data** | **Array&lt;{ [key: string]: any; }&gt;** | Table data | [default to undefined]
**title** | **string** |  | [optional] [default to undefined]
**x_column** | **string** |  | [optional] [default to undefined]
**y_columns** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { TableToChartRequest } from './api';

const instance: TableToChartRequest = {
    chart_type,
    data,
    title,
    x_column,
    y_columns,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
