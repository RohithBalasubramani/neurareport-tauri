# SpreadsheetResponse

Spreadsheet response model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **string** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**owner_id** | **string** |  | [default to undefined]
**sheets** | [**Array&lt;SheetResponse&gt;**](SheetResponse.md) |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]

## Example

```typescript
import { SpreadsheetResponse } from './api';

const instance: SpreadsheetResponse = {
    created_at,
    id,
    metadata,
    name,
    owner_id,
    sheets,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
