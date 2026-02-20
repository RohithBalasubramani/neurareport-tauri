# CollectionUpdate

Request to update a collection.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**color** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**document_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**icon** | **string** |  | [optional] [default to undefined]
**is_smart** | **boolean** |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**smart_filter** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { CollectionUpdate } from './api';

const instance: CollectionUpdate = {
    color,
    description,
    document_ids,
    icon,
    is_smart,
    name,
    smart_filter,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
