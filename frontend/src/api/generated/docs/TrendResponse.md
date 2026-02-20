# TrendResponse

Response containing trend analysis and forecast.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**forecast** | [**Array&lt;ForecastPoint&gt;**](ForecastPoint.md) |  | [default to undefined]
**method_used** | [**ForecastMethod**](ForecastMethod.md) |  | [default to undefined]
**model_accuracy** | **number** |  | [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**trend** | [**TrendResult**](TrendResult.md) |  | [default to undefined]

## Example

```typescript
import { TrendResponse } from './api';

const instance: TrendResponse = {
    forecast,
    method_used,
    model_accuracy,
    processing_time_ms,
    trend,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
