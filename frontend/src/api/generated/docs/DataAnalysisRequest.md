# DataAnalysisRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | **Array&lt;{ [key: string]: any; }&gt;** | Data to analyze | [default to undefined]
**data_description** | **string** |  | [optional] [default to undefined]
**generate_charts** | **boolean** | Generate chart suggestions | [optional] [default to true]
**question** | **string** | Question about the data | [default to undefined]

## Example

```typescript
import { DataAnalysisRequest } from './api';

const instance: DataAnalysisRequest = {
    data,
    data_description,
    generate_charts,
    question,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
