# KnowledgeGraphResponse

Knowledge graph response model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**edges** | [**Array&lt;KnowledgeGraphEdge&gt;**](KnowledgeGraphEdge.md) |  | [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**nodes** | [**Array&lt;KnowledgeGraphNode&gt;**](KnowledgeGraphNode.md) |  | [default to undefined]

## Example

```typescript
import { KnowledgeGraphResponse } from './api';

const instance: KnowledgeGraphResponse = {
    edges,
    metadata,
    nodes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
