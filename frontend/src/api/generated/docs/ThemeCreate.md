# ThemeCreate

Request to create a theme.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**borders** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**brand_kit_id** | **string** |  | [optional] [default to undefined]
**colors** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**mode** | **string** |  | [optional] [default to 'light']
**name** | **string** |  | [default to undefined]
**shadows** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**spacing** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**typography** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ThemeCreate } from './api';

const instance: ThemeCreate = {
    borders,
    brand_kit_id,
    colors,
    description,
    mode,
    name,
    shadows,
    spacing,
    typography,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
