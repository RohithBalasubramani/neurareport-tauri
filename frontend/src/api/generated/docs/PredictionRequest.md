# PredictionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**based_on_columns** | **Array&lt;string&gt;** | Input columns | [default to undefined]
**data** | **Array&lt;{ [key: string]: any; }&gt;** | Existing data | [default to undefined]
**target_description** | **string** | What to predict | [default to undefined]

## Example

```typescript
import { PredictionRequest } from './api';

const instance: PredictionRequest = {
    based_on_columns,
    data,
    target_description,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
