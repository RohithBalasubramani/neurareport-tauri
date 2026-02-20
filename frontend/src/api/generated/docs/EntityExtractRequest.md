# EntityExtractRequest

Request to extract entities.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **string** |  | [optional] [default to undefined]
**entity_types** | [**Array&lt;EntityType&gt;**](EntityType.md) |  | [optional] [default to undefined]
**file_path** | **string** |  | [optional] [default to undefined]
**text** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { EntityExtractRequest } from './api';

const instance: EntityExtractRequest = {
    content,
    entity_types,
    file_path,
    text,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
