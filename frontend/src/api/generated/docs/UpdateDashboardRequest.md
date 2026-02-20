# UpdateDashboardRequest

Update dashboard request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **string** |  | [optional] [default to undefined]
**filters** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**refresh_interval** | **number** |  | [optional] [default to undefined]
**theme** | **string** |  | [optional] [default to undefined]
**widgets** | [**Array&lt;DashboardWidget&gt;**](DashboardWidget.md) |  | [optional] [default to undefined]

## Example

```typescript
import { UpdateDashboardRequest } from './api';

const instance: UpdateDashboardRequest = {
    description,
    filters,
    name,
    refresh_interval,
    theme,
    widgets,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
