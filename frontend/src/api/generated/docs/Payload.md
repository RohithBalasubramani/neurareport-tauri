# Payload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**batch_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**connection_id** | **string** |  | [optional] [default to undefined]
**docx** | **boolean** |  | [optional] [default to false]
**email_message** | **string** |  | [optional] [default to undefined]
**email_recipients** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**email_subject** | **string** |  | [optional] [default to undefined]
**end_date** | **string** |  | [default to undefined]
**key_values** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**schedule_id** | **string** |  | [optional] [default to undefined]
**schedule_name** | **string** |  | [optional] [default to undefined]
**start_date** | **string** |  | [default to undefined]
**template_id** | **string** |  | [default to undefined]
**xlsx** | **boolean** |  | [optional] [default to false]

## Example

```typescript
import { Payload } from './api';

const instance: Payload = {
    batch_ids,
    connection_id,
    docx,
    email_message,
    email_recipients,
    email_subject,
    end_date,
    key_values,
    schedule_id,
    schedule_name,
    start_date,
    template_id,
    xlsx,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
