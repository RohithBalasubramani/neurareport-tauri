# DataValidationRequest

Request to add data validation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_blank** | **boolean** |  | [optional] [default to true]
**criteria** | **string** |  | [optional] [default to 'equals']
**error_message** | **string** |  | [optional] [default to undefined]
**range** | **string** |  | [default to undefined]
**show_dropdown** | **boolean** |  | [optional] [default to true]
**type** | **string** |  | [default to undefined]
**value** | **any** |  | [default to undefined]
**value2** | [****](.md) |  | [optional] [default to undefined]

## Example

```typescript
import { DataValidationRequest } from './api';

const instance: DataValidationRequest = {
    allow_blank,
    criteria,
    error_message,
    range,
    show_dropdown,
    type,
    value,
    value2,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
