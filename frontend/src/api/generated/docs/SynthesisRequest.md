# SynthesisRequest

Request to synthesize documents in a session.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**focus_topics** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**include_sources** | **boolean** |  | [optional] [default to true]
**max_length** | **number** |  | [optional] [default to 5000]
**output_format** | **string** |  | [optional] [default to 'structured']

## Example

```typescript
import { SynthesisRequest } from './api';

const instance: SynthesisRequest = {
    focus_topics,
    include_sources,
    max_length,
    output_format,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
