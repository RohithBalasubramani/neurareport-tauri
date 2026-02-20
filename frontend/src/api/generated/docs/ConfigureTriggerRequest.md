# ConfigureTriggerRequest

Request to configure a workflow trigger.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**trigger_type** | [**TriggerType**](TriggerType.md) |  | [default to undefined]

## Example

```typescript
import { ConfigureTriggerRequest } from './api';

const instance: ConfigureTriggerRequest = {
    config,
    trigger_type,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
