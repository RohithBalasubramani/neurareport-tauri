# ReceiptScanResponse

Scanned receipt data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**card_last_four** | **string** |  | [optional] [default to undefined]
**category** | **string** |  | [optional] [default to undefined]
**confidence_score** | **number** |  | [default to undefined]
**currency** | **string** |  | [optional] [default to 'USD']
**date** | **string** |  | [optional] [default to undefined]
**items** | [**Array&lt;ReceiptItem&gt;**](ReceiptItem.md) |  | [optional] [default to undefined]
**merchant_address** | **string** |  | [optional] [default to undefined]
**merchant_name** | **string** |  | [optional] [default to undefined]
**merchant_phone** | **string** |  | [optional] [default to undefined]
**payment_method** | **string** |  | [optional] [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**raw_text** | **string** |  | [optional] [default to undefined]
**subtotal** | **number** |  | [optional] [default to undefined]
**tax** | **number** |  | [optional] [default to undefined]
**time** | **string** |  | [optional] [default to undefined]
**tip** | **number** |  | [optional] [default to undefined]
**total** | **number** |  | [default to undefined]

## Example

```typescript
import { ReceiptScanResponse } from './api';

const instance: ReceiptScanResponse = {
    card_last_four,
    category,
    confidence_score,
    currency,
    date,
    items,
    merchant_address,
    merchant_name,
    merchant_phone,
    payment_method,
    processing_time_ms,
    raw_text,
    subtotal,
    tax,
    time,
    tip,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
