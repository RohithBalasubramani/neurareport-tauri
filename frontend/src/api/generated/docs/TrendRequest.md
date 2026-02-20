# TrendRequest

Request for trend analysis and forecasting.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence_level** | **number** |  | [optional] [default to 0.95]
**data** | [**DataSeries**](DataSeries.md) |  | [default to undefined]
**detect_change_points** | **boolean** |  | [optional] [default to true]
**detect_seasonality** | **boolean** |  | [optional] [default to true]
**forecast_periods** | **number** |  | [optional] [default to 10]
**method** | [**ForecastMethod**](ForecastMethod.md) |  | [optional] [default to undefined]

## Example

```typescript
import { TrendRequest } from './api';

const instance: TrendRequest = {
    confidence_level,
    data,
    detect_change_points,
    detect_seasonality,
    forecast_periods,
    method,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
