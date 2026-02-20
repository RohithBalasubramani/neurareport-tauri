# WhatIfResult

Result of a what-if scenario.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**affected_metrics** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**change** | **number** |  | [default to undefined]
**change_percentage** | **number** |  | [default to undefined]
**confidence** | **number** |  | [default to undefined]
**original_value** | **number** |  | [default to undefined]
**projected_value** | **number** |  | [default to undefined]
**scenario_name** | **string** |  | [default to undefined]

## Example

```typescript
import { WhatIfResult } from './api';

const instance: WhatIfResult = {
    affected_metrics,
    change,
    change_percentage,
    confidence,
    original_value,
    projected_value,
    scenario_name,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
