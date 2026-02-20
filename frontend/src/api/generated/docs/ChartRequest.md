# ChartRequest

Request model for generating charts.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chart_type** | **string** |  | [optional] [default to undefined]
**include_forecasts** | **boolean** |  | [optional] [default to false]
**include_trends** | **boolean** |  | [optional] [default to true]
**query** | **string** |  | [default to undefined]

## Example

```typescript
import { ChartRequest } from './api';

const instance: ChartRequest = {
    chart_type,
    include_forecasts,
    include_trends,
    query,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
