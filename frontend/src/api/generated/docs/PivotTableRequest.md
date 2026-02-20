# PivotTableRequest

Request to create pivot table.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column_fields** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**filters** | [**Array&lt;PivotFilter&gt;**](PivotFilter.md) |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to 'PivotTable1']
**row_fields** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**show_col_totals** | **boolean** |  | [optional] [default to true]
**show_grand_totals** | **boolean** |  | [optional] [default to true]
**show_row_totals** | **boolean** |  | [optional] [default to true]
**source_range** | **string** |  | [default to undefined]
**value_fields** | [**Array&lt;PivotValue&gt;**](PivotValue.md) |  | [default to undefined]

## Example

```typescript
import { PivotTableRequest } from './api';

const instance: PivotTableRequest = {
    column_fields,
    filters,
    name,
    row_fields,
    show_col_totals,
    show_grand_totals,
    show_row_totals,
    source_range,
    value_fields,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
