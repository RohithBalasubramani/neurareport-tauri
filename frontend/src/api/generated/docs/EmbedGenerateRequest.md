# EmbedGenerateRequest

Request to generate embed code.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_download** | **boolean** |  | [optional] [default to false]
**allow_print** | **boolean** |  | [optional] [default to false]
**document_id** | **string** |  | [default to undefined]
**height** | **number** |  | [optional] [default to 600]
**show_toolbar** | **boolean** |  | [optional] [default to true]
**theme** | **string** |  | [optional] [default to 'light']
**width** | **number** |  | [optional] [default to 800]

## Example

```typescript
import { EmbedGenerateRequest } from './api';

const instance: EmbedGenerateRequest = {
    allow_download,
    allow_print,
    document_id,
    height,
    show_toolbar,
    theme,
    width,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
