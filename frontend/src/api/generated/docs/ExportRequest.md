# ExportRequest

Request model for exporting analysis.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | **string** |  | [optional] [default to 'json']
**include_charts** | **boolean** |  | [optional] [default to true]
**include_raw_data** | **boolean** |  | [optional] [default to true]

## Example

```typescript
import { ExportRequest } from './api';

const instance: ExportRequest = {
    format,
    include_charts,
    include_raw_data,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
