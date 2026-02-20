# WhatIfResponse

Response containing what-if analysis results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**baseline** | **number** |  | [default to undefined]
**model_r_squared** | **number** |  | [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**results** | [**Array&lt;WhatIfResult&gt;**](WhatIfResult.md) |  | [default to undefined]

## Example

```typescript
import { WhatIfResponse } from './api';

const instance: WhatIfResponse = {
    baseline,
    model_r_squared,
    processing_time_ms,
    results,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
