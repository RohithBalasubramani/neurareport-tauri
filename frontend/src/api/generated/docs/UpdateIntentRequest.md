# UpdateIntentRequest

Update an intent with outcome.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**status** | **string** | Intent outcome status (e.g., \&#39;completed\&#39;, \&#39;failed\&#39;, \&#39;cancelled\&#39;) | [default to undefined]

## Example

```typescript
import { UpdateIntentRequest } from './api';

const instance: UpdateIntentRequest = {
    result,
    status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
