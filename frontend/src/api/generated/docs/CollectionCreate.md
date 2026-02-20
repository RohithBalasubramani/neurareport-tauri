# CollectionCreate

Request to create a collection.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**color** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**document_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**icon** | **string** |  | [optional] [default to undefined]
**is_smart** | **boolean** |  | [optional] [default to false]
**name** | **string** |  | [default to undefined]
**smart_filter** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { CollectionCreate } from './api';

const instance: CollectionCreate = {
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
