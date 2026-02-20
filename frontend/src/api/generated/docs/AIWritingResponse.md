# AIWritingResponse

Response for AI writing operations.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **number** |  | [optional] [default to 1.0]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**original_text** | **string** |  | [default to undefined]
**result_text** | **string** |  | [default to undefined]
**suggestions** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { AIWritingResponse } from './api';

const instance: AIWritingResponse = {
    confidence,
    metadata,
    original_text,
    result_text,
    suggestions,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
