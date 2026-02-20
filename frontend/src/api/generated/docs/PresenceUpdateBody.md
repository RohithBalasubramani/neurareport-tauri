# PresenceUpdateBody

Request body for updating user presence.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cursor_position** | **number** |  | [optional] [default to undefined]
**selection** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**user_id** | **string** |  | [default to undefined]

## Example

```typescript
import { PresenceUpdateBody } from './api';

const instance: PresenceUpdateBody = {
    cursor_position,
    selection,
    user_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
