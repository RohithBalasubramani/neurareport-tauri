# InsightsRequest

Request for generating insights.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**columns** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**context** | **string** |  | [optional] [default to undefined]
**data** | [**Array&lt;DataSeries&gt;**](DataSeries.md) |  | [default to undefined]
**insight_types** | [**Array&lt;InsightType&gt;**](InsightType.md) |  | [optional] [default to undefined]
**max_insights** | **number** |  | [optional] [default to 10]
**time_column** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { InsightsRequest } from './api';

const instance: InsightsRequest = {
    columns,
    context,
    data,
    insight_types,
    max_insights,
    time_column,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
