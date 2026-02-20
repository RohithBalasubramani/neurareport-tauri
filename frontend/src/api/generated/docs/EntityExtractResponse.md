# EntityExtractResponse

Entity extraction result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entities** | [**Array&lt;ExtractedEntity&gt;**](ExtractedEntity.md) |  | [optional] [default to undefined]
**entity_counts** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]

## Example

```typescript
import { EntityExtractResponse } from './api';

const instance: EntityExtractResponse = {
    entities,
    entity_counts,
    processing_time_ms,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
