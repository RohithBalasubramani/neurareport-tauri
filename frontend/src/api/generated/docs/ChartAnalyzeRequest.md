# ChartAnalyzeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column_descriptions** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**data** | **Array&lt;{ [key: string]: any; }&gt;** |  | [default to undefined]
**max_suggestions** | **number** |  | [optional] [default to 3]

## Example

```typescript
import { ChartAnalyzeRequest } from './api';

const instance: ChartAnalyzeRequest = {
    column_descriptions,
    data,
    max_suggestions,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
