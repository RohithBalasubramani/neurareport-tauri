# KnowledgeGraphRequest

Request to build a knowledge graph.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**depth** | **number** |  | [optional] [default to 2]
**document_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**include_entities** | **boolean** |  | [optional] [default to true]
**include_relationships** | **boolean** |  | [optional] [default to true]

## Example

```typescript
import { KnowledgeGraphRequest } from './api';

const instance: KnowledgeGraphRequest = {
    depth,
    document_ids,
    include_entities,
    include_relationships,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
