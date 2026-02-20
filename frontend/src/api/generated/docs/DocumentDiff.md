# DocumentDiff

A difference between documents.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**diff_type** | [**DiffType**](DiffType.md) |  | [default to undefined]
**modified_text** | **string** |  | [optional] [default to undefined]
**original_text** | **string** |  | [optional] [default to undefined]
**page_number** | **number** |  | [optional] [default to undefined]
**section** | **string** |  | [optional] [default to undefined]
**significance** | **string** |  | [optional] [default to 'low']

## Example

```typescript
import { DocumentDiff } from './api';

const instance: DocumentDiff = {
    diff_type,
    modified_text,
    original_text,
    page_number,
    section,
    significance,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
