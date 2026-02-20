# NL2SQLGenerateRequest

Request to generate SQL from natural language.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection_id** | **string** |  | [default to undefined]
**context** | **string** |  | [optional] [default to undefined]
**question** | **string** |  | [default to undefined]
**tables** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { NL2SQLGenerateRequest } from './api';

const instance: NL2SQLGenerateRequest = {
    connection_id,
    context,
    question,
    tables,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
