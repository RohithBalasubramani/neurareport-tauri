# BackendAppApiRoutesAgentsV2ResearchRequest

Request to run the research agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**depth** | **string** | Research depth - quick (overview), moderate (balanced), comprehensive (detailed) | [optional] [default to DepthEnum_comprehensive]
**focus_areas** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**idempotency_key** | **string** |  | [optional] [default to undefined]
**max_sections** | **number** | Maximum number of sections in the report | [optional] [default to 5]
**priority** | **number** | Task priority (0&#x3D;lowest, 10&#x3D;highest) | [optional] [default to 0]
**sync** | **boolean** | If true, wait for completion. If false, return immediately. | [optional] [default to true]
**topic** | **string** | Topic to research (must be at least 2 words) | [default to undefined]
**webhook_url** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { BackendAppApiRoutesAgentsV2ResearchRequest } from './api';

const instance: BackendAppApiRoutesAgentsV2ResearchRequest = {
    depth,
    focus_areas,
    idempotency_key,
    max_sections,
    priority,
    sync,
    topic,
    webhook_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
