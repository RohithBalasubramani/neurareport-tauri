# AnomalyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**columns_to_analyze** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**data** | **Array&lt;{ [key: string]: any; }&gt;** | Data to analyze | [default to undefined]
**sensitivity** | **string** | Detection sensitivity | [optional] [default to 'medium']

## Example

```typescript
import { AnomalyRequest } from './api';

const instance: AnomalyRequest = {
    columns_to_analyze,
    data,
    sensitivity,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
