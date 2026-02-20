# AnomaliesResponse

Response containing detected anomalies.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anomalies** | [**Array&lt;Anomaly&gt;**](Anomaly.md) |  | [default to undefined]
**anomaly_rate** | **number** |  | [default to undefined]
**baseline_stats** | **{ [key: string]: number; }** |  | [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]

## Example

```typescript
import { AnomaliesResponse } from './api';

const instance: AnomaliesResponse = {
    anomalies,
    anomaly_rate,
    baseline_stats,
    processing_time_ms,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
