# ScheduleUpdatePayload

All fields optional for partial updates.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **boolean** |  | [optional] [default to undefined]
**batch_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**docx** | **boolean** |  | [optional] [default to undefined]
**email_message** | **string** |  | [optional] [default to undefined]
**email_recipients** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**email_subject** | **string** |  | [optional] [default to undefined]
**end_date** | **string** |  | [optional] [default to undefined]
**frequency** | **string** |  | [optional] [default to undefined]
**interval_minutes** | **number** |  | [optional] [default to undefined]
**key_values** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**start_date** | **string** |  | [optional] [default to undefined]
**xlsx** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { ScheduleUpdatePayload } from './api';

const instance: ScheduleUpdatePayload = {
    active,
    batch_ids,
    docx,
    email_message,
    email_recipients,
    email_subject,
    end_date,
    frequency,
    interval_minutes,
    key_values,
    name,
    start_date,
    xlsx,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
