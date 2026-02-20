# BrandKitCreate

Request to create a brand kit.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accent_color** | **string** |  | [optional] [default to '#ff9800']
**background_color** | **string** |  | [optional] [default to '#ffffff']
**colors** | [**Array&lt;BrandColor&gt;**](BrandColor.md) |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**favicon_url** | **string** |  | [optional] [default to undefined]
**logo_dark_url** | **string** |  | [optional] [default to undefined]
**logo_url** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**primary_color** | **string** |  | [optional] [default to '#1976d2']
**secondary_color** | **string** |  | [optional] [default to '#dc004e']
**text_color** | **string** |  | [optional] [default to '#333333']
**typography** | [**Typography**](Typography.md) |  | [optional] [default to undefined]

## Example

```typescript
import { BrandKitCreate } from './api';

const instance: BrandKitCreate = {
    accent_color,
    background_color,
    colors,
    description,
    favicon_url,
    logo_dark_url,
    logo_url,
    name,
    primary_color,
    secondary_color,
    text_color,
    typography,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
