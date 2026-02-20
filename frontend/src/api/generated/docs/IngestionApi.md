# IngestionApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**clipSelectionApiV1IngestionClipSelectionPost**](#clipselectionapiv1ingestionclipselectionpost) | **POST** /api/v1/ingestion/clip/selection | Clip Selection|
|[**clipWebPageApiV1IngestionClipUrlPost**](#clipwebpageapiv1ingestionclipurlpost) | **POST** /api/v1/ingestion/clip/url | Clip Web Page|
|[**connectImapAccountApiV1IngestionEmailImapConnectPost**](#connectimapaccountapiv1ingestionemailimapconnectpost) | **POST** /api/v1/ingestion/email/imap/connect | Connect Imap Account|
|[**createFolderWatcherApiV1IngestionWatchersPost**](#createfolderwatcherapiv1ingestionwatcherspost) | **POST** /api/v1/ingestion/watchers | Create Folder Watcher|
|[**deleteWatcherApiV1IngestionWatchersWatcherIdDelete**](#deletewatcherapiv1ingestionwatcherswatcheriddelete) | **DELETE** /api/v1/ingestion/watchers/{watcher_id} | Delete Watcher|
|[**detectFileTypeApiV1IngestionDetectTypePost**](#detectfiletypeapiv1ingestiondetecttypepost) | **POST** /api/v1/ingestion/detect-type | Detect File Type|
|[**generateInboxAddressApiV1IngestionEmailInboxPost**](#generateinboxaddressapiv1ingestionemailinboxpost) | **POST** /api/v1/ingestion/email/inbox | Generate Inbox Address|
|[**getTranscriptionStatusApiV1IngestionTranscribeJobIdGet**](#gettranscriptionstatusapiv1ingestiontranscribejobidget) | **GET** /api/v1/ingestion/transcribe/{job_id} | Get Transcription Status|
|[**getWatcherStatusApiV1IngestionWatchersWatcherIdGet**](#getwatcherstatusapiv1ingestionwatcherswatcheridget) | **GET** /api/v1/ingestion/watchers/{watcher_id} | Get Watcher Status|
|[**ingestEmailApiV1IngestionEmailIngestPost**](#ingestemailapiv1ingestionemailingestpost) | **POST** /api/v1/ingestion/email/ingest | Ingest Email|
|[**ingestFromUrlApiV1IngestionUrlPost**](#ingestfromurlapiv1ingestionurlpost) | **POST** /api/v1/ingestion/url | Ingest From Url|
|[**ingestStructuredDataApiV1IngestionStructuredPost**](#ingeststructureddataapiv1ingestionstructuredpost) | **POST** /api/v1/ingestion/structured | Ingest Structured Data|
|[**listFolderWatchersApiV1IngestionWatchersGet**](#listfolderwatchersapiv1ingestionwatchersget) | **GET** /api/v1/ingestion/watchers | List Folder Watchers|
|[**listImapAccountsApiV1IngestionEmailImapAccountsGet**](#listimapaccountsapiv1ingestionemailimapaccountsget) | **GET** /api/v1/ingestion/email/imap/accounts | List Imap Accounts|
|[**listSupportedTypesApiV1IngestionSupportedTypesGet**](#listsupportedtypesapiv1ingestionsupportedtypesget) | **GET** /api/v1/ingestion/supported-types | List Supported Types|
|[**parseEmailApiV1IngestionEmailParsePost**](#parseemailapiv1ingestionemailparsepost) | **POST** /api/v1/ingestion/email/parse | Parse Email|
|[**scanWatchedFolderApiV1IngestionWatchersWatcherIdScanPost**](#scanwatchedfolderapiv1ingestionwatcherswatcheridscanpost) | **POST** /api/v1/ingestion/watchers/{watcher_id}/scan | Scan Watched Folder|
|[**startWatcherApiV1IngestionWatchersWatcherIdStartPost**](#startwatcherapiv1ingestionwatcherswatcheridstartpost) | **POST** /api/v1/ingestion/watchers/{watcher_id}/start | Start Watcher|
|[**stopWatcherApiV1IngestionWatchersWatcherIdStopPost**](#stopwatcherapiv1ingestionwatcherswatcheridstoppost) | **POST** /api/v1/ingestion/watchers/{watcher_id}/stop | Stop Watcher|
|[**syncImapAccountApiV1IngestionEmailImapAccountsAccountIdSyncPost**](#syncimapaccountapiv1ingestionemailimapaccountsaccountidsyncpost) | **POST** /api/v1/ingestion/email/imap/accounts/{account_id}/sync | Sync Imap Account|
|[**transcribeFileApiV1IngestionTranscribePost**](#transcribefileapiv1ingestiontranscribepost) | **POST** /api/v1/ingestion/transcribe | Transcribe File|
|[**transcribeVoiceMemoApiV1IngestionTranscribeVoiceMemoPost**](#transcribevoicememoapiv1ingestiontranscribevoicememopost) | **POST** /api/v1/ingestion/transcribe/voice-memo | Transcribe Voice Memo|
|[**uploadBulkApiV1IngestionUploadBulkPost**](#uploadbulkapiv1ingestionuploadbulkpost) | **POST** /api/v1/ingestion/upload/bulk | Upload Bulk|
|[**uploadFileApiV1IngestionUploadPost**](#uploadfileapiv1ingestionuploadpost) | **POST** /api/v1/ingestion/upload | Upload File|
|[**uploadZipApiV1IngestionUploadZipPost**](#uploadzipapiv1ingestionuploadzippost) | **POST** /api/v1/ingestion/upload/zip | Upload Zip|

# **clipSelectionApiV1IngestionClipSelectionPost**
> any clipSelectionApiV1IngestionClipSelectionPost(clipSelectionRequest)

Clip a user-selected portion of a page.  Returns:     ClippedContent with selected content

### Example

```typescript
import {
    IngestionApi,
    Configuration,
    ClipSelectionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let clipSelectionRequest: ClipSelectionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.clipSelectionApiV1IngestionClipSelectionPost(
    clipSelectionRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **clipSelectionRequest** | **ClipSelectionRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **clipWebPageApiV1IngestionClipUrlPost**
> any clipWebPageApiV1IngestionClipUrlPost(clipUrlRequest)

Clip content from a web page.  Returns:     ClippedContent with extracted content

### Example

```typescript
import {
    IngestionApi,
    Configuration,
    ClipUrlRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let clipUrlRequest: ClipUrlRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.clipWebPageApiV1IngestionClipUrlPost(
    clipUrlRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **clipUrlRequest** | **ClipUrlRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **connectImapAccountApiV1IngestionEmailImapConnectPost**
> any connectImapAccountApiV1IngestionEmailImapConnectPost(imapConnectRequest)

Connect an IMAP email account.  Tests the connection and stores the account configuration.  Returns:     Connection result with account ID

### Example

```typescript
import {
    IngestionApi,
    Configuration,
    ImapConnectRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let imapConnectRequest: ImapConnectRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.connectImapAccountApiV1IngestionEmailImapConnectPost(
    imapConnectRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **imapConnectRequest** | **ImapConnectRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createFolderWatcherApiV1IngestionWatchersPost**
> any createFolderWatcherApiV1IngestionWatchersPost(createWatcherRequest)

Create a new folder watcher.  Returns:     WatcherStatus

### Example

```typescript
import {
    IngestionApi,
    Configuration,
    CreateWatcherRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let createWatcherRequest: CreateWatcherRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createFolderWatcherApiV1IngestionWatchersPost(
    createWatcherRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createWatcherRequest** | **CreateWatcherRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteWatcherApiV1IngestionWatchersWatcherIdDelete**
> any deleteWatcherApiV1IngestionWatchersWatcherIdDelete()

Delete a folder watcher.

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let watcherId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteWatcherApiV1IngestionWatchersWatcherIdDelete(
    watcherId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **watcherId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **detectFileTypeApiV1IngestionDetectTypePost**
> any detectFileTypeApiV1IngestionDetectTypePost()

Detect the type of an uploaded file.  Returns:     Detected file type and metadata

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let file: File; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.detectFileTypeApiV1IngestionDetectTypePost(
    file,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateInboxAddressApiV1IngestionEmailInboxPost**
> any generateInboxAddressApiV1IngestionEmailInboxPost(generateInboxRequest)

Generate a unique email inbox address for forwarding.  Returns:     Email address for forwarding

### Example

```typescript
import {
    IngestionApi,
    Configuration,
    GenerateInboxRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let generateInboxRequest: GenerateInboxRequest; //
let userId: string; // (optional) (default to 'default')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateInboxAddressApiV1IngestionEmailInboxPost(
    generateInboxRequest,
    userId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **generateInboxRequest** | **GenerateInboxRequest**|  | |
| **userId** | [**string**] |  | (optional) defaults to 'default'|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTranscriptionStatusApiV1IngestionTranscribeJobIdGet**
> any getTranscriptionStatusApiV1IngestionTranscribeJobIdGet()

Get the status of a transcription job.  Returns:     Job status, progress, and result when complete

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTranscriptionStatusApiV1IngestionTranscribeJobIdGet(
    jobId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWatcherStatusApiV1IngestionWatchersWatcherIdGet**
> any getWatcherStatusApiV1IngestionWatchersWatcherIdGet()

Get status of a folder watcher.  Returns:     WatcherStatus

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let watcherId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWatcherStatusApiV1IngestionWatchersWatcherIdGet(
    watcherId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **watcherId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **ingestEmailApiV1IngestionEmailIngestPost**
> any ingestEmailApiV1IngestionEmailIngestPost()

Ingest a raw email file (.eml).  Returns:     EmailDocumentResult with created document

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let file: File; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let includeAttachments: boolean; // (optional) (default to true)

const { status, data } = await apiInstance.ingestEmailApiV1IngestionEmailIngestPost(
    file,
    xApiKey,
    includeAttachments
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **includeAttachments** | [**boolean**] |  | (optional) defaults to true|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **ingestFromUrlApiV1IngestionUrlPost**
> any ingestFromUrlApiV1IngestionUrlPost(ingestUrlRequest)

Download and ingest a file from a URL.  Returns:     IngestionResult with document details

### Example

```typescript
import {
    IngestionApi,
    Configuration,
    IngestUrlRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let ingestUrlRequest: IngestUrlRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.ingestFromUrlApiV1IngestionUrlPost(
    ingestUrlRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **ingestUrlRequest** | **IngestUrlRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **ingestStructuredDataApiV1IngestionStructuredPost**
> any ingestStructuredDataApiV1IngestionStructuredPost(ingestStructuredDataRequest)

Import structured data (JSON/XML/YAML) as an editable table.  Returns:     StructuredDataImport with table details

### Example

```typescript
import {
    IngestionApi,
    Configuration,
    IngestStructuredDataRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let ingestStructuredDataRequest: IngestStructuredDataRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.ingestStructuredDataApiV1IngestionStructuredPost(
    ingestStructuredDataRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **ingestStructuredDataRequest** | **IngestStructuredDataRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listFolderWatchersApiV1IngestionWatchersGet**
> any listFolderWatchersApiV1IngestionWatchersGet()

List all folder watchers.  Returns:     List of WatcherStatus

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listFolderWatchersApiV1IngestionWatchersGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listImapAccountsApiV1IngestionEmailImapAccountsGet**
> any listImapAccountsApiV1IngestionEmailImapAccountsGet()

List connected IMAP email accounts.  Returns:     List of connected IMAP accounts

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listImapAccountsApiV1IngestionEmailImapAccountsGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listSupportedTypesApiV1IngestionSupportedTypesGet**
> any listSupportedTypesApiV1IngestionSupportedTypesGet()

List all supported file types for ingestion.  Returns:     List of supported file types

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSupportedTypesApiV1IngestionSupportedTypesGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **parseEmailApiV1IngestionEmailParsePost**
> any parseEmailApiV1IngestionEmailParsePost()

Parse an email and extract structured data.  Returns:     Parsed email with action items and links

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let file: File; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let extractActionItems: boolean; // (optional) (default to true)

const { status, data } = await apiInstance.parseEmailApiV1IngestionEmailParsePost(
    file,
    xApiKey,
    extractActionItems
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **extractActionItems** | [**boolean**] |  | (optional) defaults to true|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scanWatchedFolderApiV1IngestionWatchersWatcherIdScanPost**
> any scanWatchedFolderApiV1IngestionWatchersWatcherIdScanPost()

Manually scan a watched folder for existing files.  Returns:     List of FileEvents

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let watcherId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scanWatchedFolderApiV1IngestionWatchersWatcherIdScanPost(
    watcherId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **watcherId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **startWatcherApiV1IngestionWatchersWatcherIdStartPost**
> any startWatcherApiV1IngestionWatchersWatcherIdStartPost()

Start a folder watcher.

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let watcherId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.startWatcherApiV1IngestionWatchersWatcherIdStartPost(
    watcherId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **watcherId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stopWatcherApiV1IngestionWatchersWatcherIdStopPost**
> any stopWatcherApiV1IngestionWatchersWatcherIdStopPost()

Stop a folder watcher.

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let watcherId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.stopWatcherApiV1IngestionWatchersWatcherIdStopPost(
    watcherId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **watcherId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **syncImapAccountApiV1IngestionEmailImapAccountsAccountIdSyncPost**
> any syncImapAccountApiV1IngestionEmailImapAccountsAccountIdSyncPost()

Sync emails from an IMAP account.  Triggers email synchronisation for the specified account.  Returns:     Sync job status

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let accountId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.syncImapAccountApiV1IngestionEmailImapAccountsAccountIdSyncPost(
    accountId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **accountId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **transcribeFileApiV1IngestionTranscribePost**
> any transcribeFileApiV1IngestionTranscribePost()

Transcribe an audio or video file.  Returns:     TranscriptionResult with full transcript

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let file: File; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let diarizeSpeakers: boolean; // (optional) (default to false)
let includeTimestamps: boolean; // (optional) (default to true)
let language: string; // (optional) (default to 'auto')
let outputFormat: string; // (optional) (default to 'html')

const { status, data } = await apiInstance.transcribeFileApiV1IngestionTranscribePost(
    file,
    xApiKey,
    diarizeSpeakers,
    includeTimestamps,
    language,
    outputFormat
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **diarizeSpeakers** | [**boolean**] |  | (optional) defaults to false|
| **includeTimestamps** | [**boolean**] |  | (optional) defaults to true|
| **language** | [**string**] |  | (optional) defaults to 'auto'|
| **outputFormat** | [**string**] |  | (optional) defaults to 'html'|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **transcribeVoiceMemoApiV1IngestionTranscribeVoiceMemoPost**
> any transcribeVoiceMemoApiV1IngestionTranscribeVoiceMemoPost()

Transcribe a voice memo with intelligent extraction.  Returns:     VoiceMemoResult with transcript and extracted items

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let file: File; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let extractActionItems: boolean; // (optional) (default to true)
let extractKeyPoints: boolean; // (optional) (default to true)

const { status, data } = await apiInstance.transcribeVoiceMemoApiV1IngestionTranscribeVoiceMemoPost(
    file,
    xApiKey,
    extractActionItems,
    extractKeyPoints
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **extractActionItems** | [**boolean**] |  | (optional) defaults to true|
| **extractKeyPoints** | [**boolean**] |  | (optional) defaults to true|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **uploadBulkApiV1IngestionUploadBulkPost**
> any uploadBulkApiV1IngestionUploadBulkPost()

Upload multiple files at once.  Returns:     List of IngestionResults

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let files: Array<File>; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let collection: string; // (optional) (default to '')
let tags: string; // (optional) (default to '')

const { status, data } = await apiInstance.uploadBulkApiV1IngestionUploadBulkPost(
    files,
    xApiKey,
    collection,
    tags
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **files** | **Array&lt;File&gt;** |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **collection** | [**string**] |  | (optional) defaults to ''|
| **tags** | [**string**] |  | (optional) defaults to ''|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **uploadFileApiV1IngestionUploadPost**
> any uploadFileApiV1IngestionUploadPost()

Upload and ingest a file with auto-detection.  Returns:     IngestionResult with document details

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let file: File; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let autoOcr: boolean; // (optional) (default to true)
let collection: string; // (optional) (default to '')
let generatePreview: boolean; // (optional) (default to true)
let tags: string; // (optional) (default to '')

const { status, data } = await apiInstance.uploadFileApiV1IngestionUploadPost(
    file,
    xApiKey,
    autoOcr,
    collection,
    generatePreview,
    tags
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **autoOcr** | [**boolean**] |  | (optional) defaults to true|
| **collection** | [**string**] |  | (optional) defaults to ''|
| **generatePreview** | [**boolean**] |  | (optional) defaults to true|
| **tags** | [**string**] |  | (optional) defaults to ''|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **uploadZipApiV1IngestionUploadZipPost**
> any uploadZipApiV1IngestionUploadZipPost()

Upload and extract a ZIP archive.  Returns:     BulkIngestionResult with all extracted documents

### Example

```typescript
import {
    IngestionApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IngestionApi(configuration);

let file: File; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let flatten: boolean; // (optional) (default to false)
let preserveStructure: boolean; // (optional) (default to true)

const { status, data } = await apiInstance.uploadZipApiV1IngestionUploadZipPost(
    file,
    xApiKey,
    flatten,
    preserveStructure
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **flatten** | [**boolean**] |  | (optional) defaults to false|
| **preserveStructure** | [**boolean**] |  | (optional) defaults to true|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

