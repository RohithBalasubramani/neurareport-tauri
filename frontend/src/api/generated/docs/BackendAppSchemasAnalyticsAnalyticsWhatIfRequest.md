# BackendAppSchemasAnalyticsAnalyticsWhatIfRequest

Request for what-if analysis.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**Array&lt;DataSeries&gt;**](DataSeries.md) |  | [default to undefined]
**model_type** | **string** |  | [optional] [default to 'linear']
**scenarios** | [**Array&lt;WhatIfScenario&gt;**](WhatIfScenario.md) |  | [default to undefined]
**target_variable** | **string** |  | [default to undefined]

## Example

```typescript
import { BackendAppSchemasAnalyticsAnalyticsWhatIfRequest } from './api';

const instance: BackendAppSchemasAnalyticsAnalyticsWhatIfRequest = {
    data,
    model_type,
    scenarios,
    target_variable,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
