# BulkExportRequest

Request to export multiple documents.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_ids** | **Array&lt;string&gt;** |  | [default to undefined]
**format** | [**ExportFormat**](ExportFormat.md) |  | [default to undefined]
**_options** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**zip_filename** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { BulkExportRequest } from './api';

const instance: BulkExportRequest = {
    document_ids,
    format,
    _options,
    zip_filename,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
