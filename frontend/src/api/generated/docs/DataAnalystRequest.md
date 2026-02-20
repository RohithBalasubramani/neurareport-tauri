# DataAnalystRequest

Request to run the data analyst agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | **Array&lt;{ [key: string]: any; }&gt;** | Tabular data as list of objects | [default to undefined]
**data_description** | **string** |  | [optional] [default to undefined]
**generate_charts** | **boolean** | Whether to suggest chart visualisations | [optional] [default to true]
**idempotency_key** | **string** |  | [optional] [default to undefined]
**priority** | **number** |  | [optional] [default to 0]
**question** | **string** | Question to answer about the data | [default to undefined]
**sync** | **boolean** |  | [optional] [default to true]
**webhook_url** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { DataAnalystRequest } from './api';

const instance: DataAnalystRequest = {
    data,
    data_description,
    generate_charts,
    idempotency_key,
    priority,
    question,
    sync,
    webhook_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
