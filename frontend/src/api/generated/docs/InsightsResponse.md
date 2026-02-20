# InsightsResponse

Response containing generated insights.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data_quality_score** | **number** |  | [default to undefined]
**insights** | [**Array&lt;Insight&gt;**](Insight.md) |  | [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**summary** | **string** |  | [default to undefined]

## Example

```typescript
import { InsightsResponse } from './api';

const instance: InsightsResponse = {
    data_quality_score,
    insights,
    processing_time_ms,
    summary,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
