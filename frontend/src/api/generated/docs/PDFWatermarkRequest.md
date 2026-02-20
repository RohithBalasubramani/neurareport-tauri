# PDFWatermarkRequest

Request to add watermark to PDF.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**color** | **string** |  | [optional] [default to '#808080']
**font_size** | **number** |  | [optional] [default to 48]
**opacity** | **number** |  | [optional] [default to 0.3]
**position** | **string** |  | [optional] [default to 'center']
**text** | **string** |  | [default to undefined]

## Example

```typescript
import { PDFWatermarkRequest } from './api';

const instance: PDFWatermarkRequest = {
    color,
    font_size,
    opacity,
    position,
    text,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
