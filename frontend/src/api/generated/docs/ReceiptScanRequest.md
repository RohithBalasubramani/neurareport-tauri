# ReceiptScanRequest

Request to scan a receipt.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**categorize_items** | **boolean** |  | [optional] [default to true]
**content** | **string** |  | [optional] [default to undefined]
**file_path** | **string** |  | [optional] [default to undefined]
**language** | **string** |  | [optional] [default to 'en']

## Example

```typescript
import { ReceiptScanRequest } from './api';

const instance: ReceiptScanRequest = {
    categorize_items,
    content,
    file_path,
    language,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
