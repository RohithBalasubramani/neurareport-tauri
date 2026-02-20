# RecordIntentRequest

Record a user intent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**correlationId** | **string** |  | [optional] [default to undefined]
**id** | **string** | Unique intent identifier | [default to undefined]
**label** | **string** |  | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**sessionId** | **string** |  | [optional] [default to undefined]
**type** | **string** | Intent type (e.g., \&#39;create\&#39;, \&#39;delete\&#39;, \&#39;export\&#39;) | [default to undefined]

## Example

```typescript
import { RecordIntentRequest } from './api';

const instance: RecordIntentRequest = {
    correlationId,
    id,
    label,
    metadata,
    sessionId,
    type,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
