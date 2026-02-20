# Anomaly

A detected anomaly.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **string** |  | [default to undefined]
**deviation** | **number** |  | [default to undefined]
**expected_value** | **number** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**index** | **number** |  | [default to undefined]
**possible_causes** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**severity** | [**AnomalySeverity**](AnomalySeverity.md) |  | [default to undefined]
**timestamp** | **string** |  | [optional] [default to undefined]
**type** | [**AnomalyType**](AnomalyType.md) |  | [default to undefined]
**value** | **number** |  | [default to undefined]

## Example

```typescript
import { Anomaly } from './api';

const instance: Anomaly = {
    description,
    deviation,
    expected_value,
    id,
    index,
    possible_causes,
    severity,
    timestamp,
    type,
    value,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
