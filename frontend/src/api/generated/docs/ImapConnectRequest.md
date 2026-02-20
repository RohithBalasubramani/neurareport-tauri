# ImapConnectRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**folder** | **string** | Mailbox folder to monitor | [optional] [default to 'INBOX']
**host** | **string** | IMAP server hostname | [default to undefined]
**password** | **string** | Account password | [default to undefined]
**port** | **number** | IMAP server port | [optional] [default to 993]
**use_ssl** | **boolean** | Use SSL/TLS | [optional] [default to true]
**username** | **string** | Account username | [default to undefined]

## Example

```typescript
import { ImapConnectRequest } from './api';

const instance: ImapConnectRequest = {
    folder,
    host,
    password,
    port,
    use_ssl,
    username,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
