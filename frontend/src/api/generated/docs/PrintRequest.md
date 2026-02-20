# PrintRequest

Request body for printing a document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**copies** | **number** |  | [optional] [default to 1]
**_options** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**printer_id** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { PrintRequest } from './api';

const instance: PrintRequest = {
    copies,
    _options,
    printer_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
