# InvoiceLineItem

Line item from an invoice.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **number** |  | [default to undefined]
**confidence** | [**ConfidenceLevel**](ConfidenceLevel.md) |  | [optional] [default to undefined]
**description** | **string** |  | [default to undefined]
**quantity** | **number** |  | [optional] [default to undefined]
**tax** | **number** |  | [optional] [default to undefined]
**unit_price** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { InvoiceLineItem } from './api';

const instance: InvoiceLineItem = {
    amount,
    confidence,
    description,
    quantity,
    tax,
    unit_price,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
