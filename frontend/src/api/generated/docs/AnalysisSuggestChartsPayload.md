# AnalysisSuggestChartsPayload

Request payload for chart suggestions on an existing analysis.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**date_range** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**include_sample_data** | **boolean** |  | [optional] [default to true]
**question** | **string** |  | [optional] [default to undefined]
**table_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { AnalysisSuggestChartsPayload } from './api';

const instance: AnalysisSuggestChartsPayload = {
    date_range,
    include_sample_data,
    question,
    table_ids,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
