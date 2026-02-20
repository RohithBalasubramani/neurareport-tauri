# DashboardResponse

Dashboard response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **string** |  | [default to undefined]
**description** | **string** |  | [default to undefined]
**filters** | **Array&lt;{ [key: string]: any; }&gt;** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**refresh_interval** | **number** |  | [default to undefined]
**theme** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**widgets** | [**Array&lt;DashboardWidget&gt;**](DashboardWidget.md) |  | [default to undefined]

## Example

```typescript
import { DashboardResponse } from './api';

const instance: DashboardResponse = {
    created_at,
    description,
    filters,
    id,
    name,
    refresh_interval,
    theme,
    updated_at,
    widgets,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
