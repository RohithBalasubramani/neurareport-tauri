# AnomaliesRequest

Request for anomaly detection.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context_window** | **number** |  | [optional] [default to 10]
**data** | [**DataSeries**](DataSeries.md) |  | [default to undefined]
**detect_collective** | **boolean** |  | [optional] [default to true]
**min_severity** | [**AnomalySeverity**](AnomalySeverity.md) |  | [optional] [default to undefined]
**sensitivity** | **number** |  | [optional] [default to 0.95]

## Example

```typescript
import { AnomaliesRequest } from './api';

const instance: AnomaliesRequest = {
    context_window,
    data,
    detect_collective,
    min_severity,
    sensitivity,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
