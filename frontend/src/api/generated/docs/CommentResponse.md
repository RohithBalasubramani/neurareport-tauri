# CommentResponse

Comment response model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_id** | **string** |  | [default to undefined]
**author_name** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**document_id** | **string** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**replies** | [**Array&lt;CommentResponse&gt;**](CommentResponse.md) |  | [optional] [default to undefined]
**resolved** | **boolean** |  | [default to undefined]
**selection_end** | **number** |  | [default to undefined]
**selection_start** | **number** |  | [default to undefined]
**text** | **string** |  | [default to undefined]

## Example

```typescript
import { CommentResponse } from './api';

const instance: CommentResponse = {
    author_id,
    author_name,
    created_at,
    document_id,
    id,
    replies,
    resolved,
    selection_end,
    selection_start,
    text,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
