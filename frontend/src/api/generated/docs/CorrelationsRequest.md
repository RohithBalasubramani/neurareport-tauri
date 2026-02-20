# CorrelationsRequest

Request for correlation analysis.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**Array&lt;DataSeries&gt;**](DataSeries.md) |  | [default to undefined]
**method** | [**CorrelationType**](CorrelationType.md) |  | [optional] [default to undefined]
**min_correlation** | **number** |  | [optional] [default to 0.3]
**significance_level** | **number** |  | [optional] [default to 0.05]

## Example

```typescript
import { CorrelationsRequest } from './api';

const instance: CorrelationsRequest = {
    data,
    method,
    min_correlation,
    significance_level,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
