# InvoiceParseRequest

Request to parse an invoice.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **string** |  | [optional] [default to undefined]
**extract_addresses** | **boolean** |  | [optional] [default to true]
**extract_line_items** | **boolean** |  | [optional] [default to true]
**file_path** | **string** |  | [optional] [default to undefined]
**language** | **string** |  | [optional] [default to 'en']

## Example

```typescript
import { InvoiceParseRequest } from './api';

const instance: InvoiceParseRequest = {
    content,
    extract_addresses,
    extract_line_items,
    file_path,
    language,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
