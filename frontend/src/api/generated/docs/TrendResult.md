# TrendResult

Result of trend analysis.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**change_points** | **Array&lt;number&gt;** |  | [optional] [default to undefined]
**description** | **string** |  | [default to undefined]
**direction** | [**TrendDirection**](TrendDirection.md) |  | [default to undefined]
**seasonality** | **string** |  | [optional] [default to undefined]
**slope** | **number** |  | [default to undefined]
**strength** | **number** |  | [default to undefined]

## Example

```typescript
import { TrendResult } from './api';

const instance: TrendResult = {
    change_points,
    description,
    direction,
    seasonality,
    slope,
    strength,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
