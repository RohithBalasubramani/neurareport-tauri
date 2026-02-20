# ExportOptions

Typed export options for format endpoints.  Known fields are validated; additional fields are passed through to the export service to maintain forward compatibility.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**footer** | **string** |  | [optional] [default to undefined]
**header** | **string** |  | [optional] [default to undefined]
**include_cover** | **boolean** |  | [optional] [default to undefined]
**include_toc** | **boolean** |  | [optional] [default to undefined]
**margin_mm** | **number** |  | [optional] [default to undefined]
**orientation** | **string** |  | [optional] [default to undefined]
**page_size** | **string** |  | [optional] [default to undefined]
**quality** | **string** |  | [optional] [default to undefined]
**watermark** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ExportOptions } from './api';

const instance: ExportOptions = {
    footer,
    header,
    include_cover,
    include_toc,
    margin_mm,
    orientation,
    page_size,
    quality,
    watermark,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
