# InvoiceParseResponse

Parsed invoice data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bill_to** | [**InvoiceAddress**](InvoiceAddress.md) |  | [optional] [default to undefined]
**confidence_score** | **number** |  | [default to undefined]
**currency** | **string** |  | [optional] [default to 'USD']
**discount** | **number** |  | [optional] [default to undefined]
**due_date** | **string** |  | [optional] [default to undefined]
**invoice_date** | **string** |  | [optional] [default to undefined]
**invoice_number** | **string** |  | [optional] [default to undefined]
**line_items** | [**Array&lt;InvoiceLineItem&gt;**](InvoiceLineItem.md) |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**payment_terms** | **string** |  | [optional] [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**raw_text** | **string** |  | [optional] [default to undefined]
**ship_to** | [**InvoiceAddress**](InvoiceAddress.md) |  | [optional] [default to undefined]
**subtotal** | **number** |  | [optional] [default to undefined]
**tax_total** | **number** |  | [optional] [default to undefined]
**total** | **number** |  | [optional] [default to undefined]
**vendor** | [**InvoiceAddress**](InvoiceAddress.md) |  | [optional] [default to undefined]

## Example

```typescript
import { InvoiceParseResponse } from './api';

const instance: InvoiceParseResponse = {
    bill_to,
    confidence_score,
    currency,
    discount,
    due_date,
    invoice_date,
    invoice_number,
    line_items,
    notes,
    payment_terms,
    processing_time_ms,
    raw_text,
    ship_to,
    subtotal,
    tax_total,
    total,
    vendor,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
