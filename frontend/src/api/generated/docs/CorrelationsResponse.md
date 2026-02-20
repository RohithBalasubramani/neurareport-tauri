# CorrelationsResponse

Response containing correlation analysis.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**correlation_matrix** | **{ [key: string]: { [key: string]: number; }; }** |  | [default to undefined]
**correlations** | [**Array&lt;CorrelationPair&gt;**](CorrelationPair.md) |  | [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**strongest_negative** | [**CorrelationPair**](CorrelationPair.md) |  | [optional] [default to undefined]
**strongest_positive** | [**CorrelationPair**](CorrelationPair.md) |  | [optional] [default to undefined]

## Example

```typescript
import { CorrelationsResponse } from './api';

const instance: CorrelationsResponse = {
    correlation_matrix,
    correlations,
    processing_time_ms,
    strongest_negative,
    strongest_positive,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
