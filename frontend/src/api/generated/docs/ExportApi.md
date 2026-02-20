# ExportApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**bulkExportApiV1ExportBulkPost**](#bulkexportapiv1exportbulkpost) | **POST** /api/v1/export/bulk | Bulk Export|
|[**bulkExportApiV1ExportBulkPost_0**](#bulkexportapiv1exportbulkpost_0) | **POST** /api/v1/export/bulk | Bulk Export|
|[**cancelExportJobApiV1ExportJobsJobIdCancelPost**](#cancelexportjobapiv1exportjobsjobidcancelpost) | **POST** /api/v1/export/jobs/{job_id}/cancel | Cancel Export Job|
|[**cancelExportJobApiV1ExportJobsJobIdCancelPost_0**](#cancelexportjobapiv1exportjobsjobidcancelpost_0) | **POST** /api/v1/export/jobs/{job_id}/cancel | Cancel Export Job|
|[**downloadBulkExportApiV1ExportBulkJobIdDownloadGet**](#downloadbulkexportapiv1exportbulkjobiddownloadget) | **GET** /api/v1/export/bulk/{job_id}/download | Download Bulk Export|
|[**downloadBulkExportApiV1ExportBulkJobIdDownloadGet_0**](#downloadbulkexportapiv1exportbulkjobiddownloadget_0) | **GET** /api/v1/export/bulk/{job_id}/download | Download Bulk Export|
|[**emailCampaignApiV1ExportDistributionEmailCampaignPost**](#emailcampaignapiv1exportdistributionemailcampaignpost) | **POST** /api/v1/export/distribution/email-campaign | Email Campaign|
|[**emailCampaignApiV1ExportDistributionEmailCampaignPost_0**](#emailcampaignapiv1exportdistributionemailcampaignpost_0) | **POST** /api/v1/export/distribution/email-campaign | Email Campaign|
|[**exportToDocxApiV1ExportDocumentIdDocxPost**](#exporttodocxapiv1exportdocumentiddocxpost) | **POST** /api/v1/export/{document_id}/docx | Export To Docx|
|[**exportToDocxApiV1ExportDocumentIdDocxPost_0**](#exporttodocxapiv1exportdocumentiddocxpost_0) | **POST** /api/v1/export/{document_id}/docx | Export To Docx|
|[**exportToEpubApiV1ExportDocumentIdEpubPost**](#exporttoepubapiv1exportdocumentidepubpost) | **POST** /api/v1/export/{document_id}/epub | Export To Epub|
|[**exportToEpubApiV1ExportDocumentIdEpubPost_0**](#exporttoepubapiv1exportdocumentidepubpost_0) | **POST** /api/v1/export/{document_id}/epub | Export To Epub|
|[**exportToHtmlApiV1ExportDocumentIdHtmlPost**](#exporttohtmlapiv1exportdocumentidhtmlpost) | **POST** /api/v1/export/{document_id}/html | Export To Html|
|[**exportToHtmlApiV1ExportDocumentIdHtmlPost_0**](#exporttohtmlapiv1exportdocumentidhtmlpost_0) | **POST** /api/v1/export/{document_id}/html | Export To Html|
|[**exportToLatexApiV1ExportDocumentIdLatexPost**](#exporttolatexapiv1exportdocumentidlatexpost) | **POST** /api/v1/export/{document_id}/latex | Export To Latex|
|[**exportToLatexApiV1ExportDocumentIdLatexPost_0**](#exporttolatexapiv1exportdocumentidlatexpost_0) | **POST** /api/v1/export/{document_id}/latex | Export To Latex|
|[**exportToMarkdownApiV1ExportDocumentIdMarkdownPost**](#exporttomarkdownapiv1exportdocumentidmarkdownpost) | **POST** /api/v1/export/{document_id}/markdown | Export To Markdown|
|[**exportToMarkdownApiV1ExportDocumentIdMarkdownPost_0**](#exporttomarkdownapiv1exportdocumentidmarkdownpost_0) | **POST** /api/v1/export/{document_id}/markdown | Export To Markdown|
|[**exportToPdfApiV1ExportDocumentIdPdfPost**](#exporttopdfapiv1exportdocumentidpdfpost) | **POST** /api/v1/export/{document_id}/pdf | Export To Pdf|
|[**exportToPdfApiV1ExportDocumentIdPdfPost_0**](#exporttopdfapiv1exportdocumentidpdfpost_0) | **POST** /api/v1/export/{document_id}/pdf | Export To Pdf|
|[**exportToPdfaApiV1ExportDocumentIdPdfaPost**](#exporttopdfaapiv1exportdocumentidpdfapost) | **POST** /api/v1/export/{document_id}/pdfa | Export To Pdfa|
|[**exportToPdfaApiV1ExportDocumentIdPdfaPost_0**](#exporttopdfaapiv1exportdocumentidpdfapost_0) | **POST** /api/v1/export/{document_id}/pdfa | Export To Pdfa|
|[**exportToPptxApiV1ExportDocumentIdPptxPost**](#exporttopptxapiv1exportdocumentidpptxpost) | **POST** /api/v1/export/{document_id}/pptx | Export To Pptx|
|[**exportToPptxApiV1ExportDocumentIdPptxPost_0**](#exporttopptxapiv1exportdocumentidpptxpost_0) | **POST** /api/v1/export/{document_id}/pptx | Export To Pptx|
|[**generateEmbedApiV1ExportDistributionEmbedDocumentIdPost**](#generateembedapiv1exportdistributionembeddocumentidpost) | **POST** /api/v1/export/distribution/embed/{document_id} | Generate Embed|
|[**generateEmbedApiV1ExportDistributionEmbedDocumentIdPost_0**](#generateembedapiv1exportdistributionembeddocumentidpost_0) | **POST** /api/v1/export/distribution/embed/{document_id} | Generate Embed|
|[**getExportJobApiV1ExportJobsJobIdGet**](#getexportjobapiv1exportjobsjobidget) | **GET** /api/v1/export/jobs/{job_id} | Get Export Job|
|[**getExportJobApiV1ExportJobsJobIdGet_0**](#getexportjobapiv1exportjobsjobidget_0) | **GET** /api/v1/export/jobs/{job_id} | Get Export Job|
|[**listEmbedTokensApiV1ExportDocumentIdEmbedTokensGet**](#listembedtokensapiv1exportdocumentidembedtokensget) | **GET** /api/v1/export/{document_id}/embed/tokens | List Embed Tokens|
|[**listEmbedTokensApiV1ExportDocumentIdEmbedTokensGet_0**](#listembedtokensapiv1exportdocumentidembedtokensget_0) | **GET** /api/v1/export/{document_id}/embed/tokens | List Embed Tokens|
|[**listExportJobsApiV1ExportJobsGet**](#listexportjobsapiv1exportjobsget) | **GET** /api/v1/export/jobs | List Export Jobs|
|[**listExportJobsApiV1ExportJobsGet_0**](#listexportjobsapiv1exportjobsget_0) | **GET** /api/v1/export/jobs | List Export Jobs|
|[**listPrintersApiV1ExportPrintersGet**](#listprintersapiv1exportprintersget) | **GET** /api/v1/export/printers | List Printers|
|[**listPrintersApiV1ExportPrintersGet_0**](#listprintersapiv1exportprintersget_0) | **GET** /api/v1/export/printers | List Printers|
|[**printDocumentApiV1ExportDocumentIdPrintPost**](#printdocumentapiv1exportdocumentidprintpost) | **POST** /api/v1/export/{document_id}/print | Print Document|
|[**printDocumentApiV1ExportDocumentIdPrintPost_0**](#printdocumentapiv1exportdocumentidprintpost_0) | **POST** /api/v1/export/{document_id}/print | Print Document|
|[**publishToPortalApiV1ExportDistributionPortalDocumentIdPost**](#publishtoportalapiv1exportdistributionportaldocumentidpost) | **POST** /api/v1/export/distribution/portal/{document_id} | Publish To Portal|
|[**publishToPortalApiV1ExportDistributionPortalDocumentIdPost_0**](#publishtoportalapiv1exportdistributionportaldocumentidpost_0) | **POST** /api/v1/export/distribution/portal/{document_id} | Publish To Portal|
|[**revokeEmbedTokenApiV1ExportEmbedTokenIdDelete**](#revokeembedtokenapiv1exportembedtokeniddelete) | **DELETE** /api/v1/export/embed/{token_id} | Revoke Embed Token|
|[**revokeEmbedTokenApiV1ExportEmbedTokenIdDelete_0**](#revokeembedtokenapiv1exportembedtokeniddelete_0) | **DELETE** /api/v1/export/embed/{token_id} | Revoke Embed Token|
|[**sendToSlackApiV1ExportDistributionSlackPost**](#sendtoslackapiv1exportdistributionslackpost) | **POST** /api/v1/export/distribution/slack | Send To Slack|
|[**sendToSlackApiV1ExportDistributionSlackPost_0**](#sendtoslackapiv1exportdistributionslackpost_0) | **POST** /api/v1/export/distribution/slack | Send To Slack|
|[**sendToTeamsApiV1ExportDistributionTeamsPost**](#sendtoteamsapiv1exportdistributionteamspost) | **POST** /api/v1/export/distribution/teams | Send To Teams|
|[**sendToTeamsApiV1ExportDistributionTeamsPost_0**](#sendtoteamsapiv1exportdistributionteamspost_0) | **POST** /api/v1/export/distribution/teams | Send To Teams|
|[**sendWebhookApiV1ExportDistributionWebhookPost**](#sendwebhookapiv1exportdistributionwebhookpost) | **POST** /api/v1/export/distribution/webhook | Send Webhook|
|[**sendWebhookApiV1ExportDistributionWebhookPost_0**](#sendwebhookapiv1exportdistributionwebhookpost_0) | **POST** /api/v1/export/distribution/webhook | Send Webhook|

# **bulkExportApiV1ExportBulkPost**
> any bulkExportApiV1ExportBulkPost(bulkExportRequest)

Export multiple documents as a ZIP file.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    BulkExportRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let bulkExportRequest: BulkExportRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkExportApiV1ExportBulkPost(
    bulkExportRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bulkExportRequest** | **BulkExportRequest**|  | |
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

# **bulkExportApiV1ExportBulkPost_0**
> any bulkExportApiV1ExportBulkPost_0(bulkExportRequest)

Export multiple documents as a ZIP file.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    BulkExportRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let bulkExportRequest: BulkExportRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkExportApiV1ExportBulkPost_0(
    bulkExportRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bulkExportRequest** | **BulkExportRequest**|  | |
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

# **cancelExportJobApiV1ExportJobsJobIdCancelPost**
> any cancelExportJobApiV1ExportJobsJobIdCancelPost()

Cancel an export job.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelExportJobApiV1ExportJobsJobIdCancelPost(
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

# **cancelExportJobApiV1ExportJobsJobIdCancelPost_0**
> any cancelExportJobApiV1ExportJobsJobIdCancelPost_0()

Cancel an export job.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelExportJobApiV1ExportJobsJobIdCancelPost_0(
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

# **downloadBulkExportApiV1ExportBulkJobIdDownloadGet**
> any downloadBulkExportApiV1ExportBulkJobIdDownloadGet()

Download the result of a bulk export job.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.downloadBulkExportApiV1ExportBulkJobIdDownloadGet(
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

# **downloadBulkExportApiV1ExportBulkJobIdDownloadGet_0**
> any downloadBulkExportApiV1ExportBulkJobIdDownloadGet_0()

Download the result of a bulk export job.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.downloadBulkExportApiV1ExportBulkJobIdDownloadGet_0(
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

# **emailCampaignApiV1ExportDistributionEmailCampaignPost**
> any emailCampaignApiV1ExportDistributionEmailCampaignPost(emailCampaignRequest)

Send documents via bulk email campaign.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    EmailCampaignRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let emailCampaignRequest: EmailCampaignRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.emailCampaignApiV1ExportDistributionEmailCampaignPost(
    emailCampaignRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **emailCampaignRequest** | **EmailCampaignRequest**|  | |
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

# **emailCampaignApiV1ExportDistributionEmailCampaignPost_0**
> any emailCampaignApiV1ExportDistributionEmailCampaignPost_0(emailCampaignRequest)

Send documents via bulk email campaign.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    EmailCampaignRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let emailCampaignRequest: EmailCampaignRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.emailCampaignApiV1ExportDistributionEmailCampaignPost_0(
    emailCampaignRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **emailCampaignRequest** | **EmailCampaignRequest**|  | |
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

# **exportToDocxApiV1ExportDocumentIdDocxPost**
> any exportToDocxApiV1ExportDocumentIdDocxPost()

Export document to Word DOCX format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToDocxApiV1ExportDocumentIdDocxPost(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToDocxApiV1ExportDocumentIdDocxPost_0**
> any exportToDocxApiV1ExportDocumentIdDocxPost_0()

Export document to Word DOCX format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToDocxApiV1ExportDocumentIdDocxPost_0(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToEpubApiV1ExportDocumentIdEpubPost**
> any exportToEpubApiV1ExportDocumentIdEpubPost()

Export document to ePub format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToEpubApiV1ExportDocumentIdEpubPost(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToEpubApiV1ExportDocumentIdEpubPost_0**
> any exportToEpubApiV1ExportDocumentIdEpubPost_0()

Export document to ePub format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToEpubApiV1ExportDocumentIdEpubPost_0(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToHtmlApiV1ExportDocumentIdHtmlPost**
> any exportToHtmlApiV1ExportDocumentIdHtmlPost()

Export document to HTML format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToHtmlApiV1ExportDocumentIdHtmlPost(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToHtmlApiV1ExportDocumentIdHtmlPost_0**
> any exportToHtmlApiV1ExportDocumentIdHtmlPost_0()

Export document to HTML format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToHtmlApiV1ExportDocumentIdHtmlPost_0(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToLatexApiV1ExportDocumentIdLatexPost**
> any exportToLatexApiV1ExportDocumentIdLatexPost()

Export document to LaTeX format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToLatexApiV1ExportDocumentIdLatexPost(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToLatexApiV1ExportDocumentIdLatexPost_0**
> any exportToLatexApiV1ExportDocumentIdLatexPost_0()

Export document to LaTeX format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToLatexApiV1ExportDocumentIdLatexPost_0(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToMarkdownApiV1ExportDocumentIdMarkdownPost**
> any exportToMarkdownApiV1ExportDocumentIdMarkdownPost()

Export document to Markdown format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToMarkdownApiV1ExportDocumentIdMarkdownPost(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToMarkdownApiV1ExportDocumentIdMarkdownPost_0**
> any exportToMarkdownApiV1ExportDocumentIdMarkdownPost_0()

Export document to Markdown format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToMarkdownApiV1ExportDocumentIdMarkdownPost_0(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToPdfApiV1ExportDocumentIdPdfPost**
> any exportToPdfApiV1ExportDocumentIdPdfPost()

Export document to PDF format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToPdfApiV1ExportDocumentIdPdfPost(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToPdfApiV1ExportDocumentIdPdfPost_0**
> any exportToPdfApiV1ExportDocumentIdPdfPost_0()

Export document to PDF format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToPdfApiV1ExportDocumentIdPdfPost_0(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToPdfaApiV1ExportDocumentIdPdfaPost**
> any exportToPdfaApiV1ExportDocumentIdPdfaPost()

Export document to PDF/A archival format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToPdfaApiV1ExportDocumentIdPdfaPost(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToPdfaApiV1ExportDocumentIdPdfaPost_0**
> any exportToPdfaApiV1ExportDocumentIdPdfaPost_0()

Export document to PDF/A archival format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToPdfaApiV1ExportDocumentIdPdfaPost_0(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToPptxApiV1ExportDocumentIdPptxPost**
> any exportToPptxApiV1ExportDocumentIdPptxPost()

Export document to PowerPoint format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToPptxApiV1ExportDocumentIdPptxPost(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **exportToPptxApiV1ExportDocumentIdPptxPost_0**
> any exportToPptxApiV1ExportDocumentIdPptxPost_0()

Export document to PowerPoint format.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    ExportOptions
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let exportOptions: ExportOptions; // (optional)

const { status, data } = await apiInstance.exportToPptxApiV1ExportDocumentIdPptxPost_0(
    documentId,
    xApiKey,
    exportOptions
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportOptions** | **ExportOptions**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **generateEmbedApiV1ExportDistributionEmbedDocumentIdPost**
> EmbedResponse generateEmbedApiV1ExportDistributionEmbedDocumentIdPost(embedGenerateRequest)

Generate embed code for a document.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    EmbedGenerateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let embedGenerateRequest: EmbedGenerateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateEmbedApiV1ExportDistributionEmbedDocumentIdPost(
    documentId,
    embedGenerateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **embedGenerateRequest** | **EmbedGenerateRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**EmbedResponse**

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

# **generateEmbedApiV1ExportDistributionEmbedDocumentIdPost_0**
> EmbedResponse generateEmbedApiV1ExportDistributionEmbedDocumentIdPost_0(embedGenerateRequest)

Generate embed code for a document.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    EmbedGenerateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let embedGenerateRequest: EmbedGenerateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateEmbedApiV1ExportDistributionEmbedDocumentIdPost_0(
    documentId,
    embedGenerateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **embedGenerateRequest** | **EmbedGenerateRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**EmbedResponse**

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

# **getExportJobApiV1ExportJobsJobIdGet**
> any getExportJobApiV1ExportJobsJobIdGet()

Get export job status.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExportJobApiV1ExportJobsJobIdGet(
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

# **getExportJobApiV1ExportJobsJobIdGet_0**
> any getExportJobApiV1ExportJobsJobIdGet_0()

Get export job status.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let jobId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExportJobApiV1ExportJobsJobIdGet_0(
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

# **listEmbedTokensApiV1ExportDocumentIdEmbedTokensGet**
> any listEmbedTokensApiV1ExportDocumentIdEmbedTokensGet()

List embed tokens for a document.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listEmbedTokensApiV1ExportDocumentIdEmbedTokensGet(
    documentId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
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

# **listEmbedTokensApiV1ExportDocumentIdEmbedTokensGet_0**
> any listEmbedTokensApiV1ExportDocumentIdEmbedTokensGet_0()

List embed tokens for a document.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listEmbedTokensApiV1ExportDocumentIdEmbedTokensGet_0(
    documentId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **documentId** | [**string**] |  | defaults to undefined|
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

# **listExportJobsApiV1ExportJobsGet**
> any listExportJobsApiV1ExportJobsGet()

List all export jobs with optional filtering.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let status: string; //Filter by job status (optional) (default to undefined)
let format: string; //Filter by export format (optional) (default to undefined)
let limit: number; //Maximum number of jobs to return (optional) (default to 50)
let offset: number; //Number of jobs to skip (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listExportJobsApiV1ExportJobsGet(
    status,
    format,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **status** | [**string**] | Filter by job status | (optional) defaults to undefined|
| **format** | [**string**] | Filter by export format | (optional) defaults to undefined|
| **limit** | [**number**] | Maximum number of jobs to return | (optional) defaults to 50|
| **offset** | [**number**] | Number of jobs to skip | (optional) defaults to 0|
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

# **listExportJobsApiV1ExportJobsGet_0**
> any listExportJobsApiV1ExportJobsGet_0()

List all export jobs with optional filtering.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let status: string; //Filter by job status (optional) (default to undefined)
let format: string; //Filter by export format (optional) (default to undefined)
let limit: number; //Maximum number of jobs to return (optional) (default to 50)
let offset: number; //Number of jobs to skip (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listExportJobsApiV1ExportJobsGet_0(
    status,
    format,
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **status** | [**string**] | Filter by job status | (optional) defaults to undefined|
| **format** | [**string**] | Filter by export format | (optional) defaults to undefined|
| **limit** | [**number**] | Maximum number of jobs to return | (optional) defaults to 50|
| **offset** | [**number**] | Number of jobs to skip | (optional) defaults to 0|
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

# **listPrintersApiV1ExportPrintersGet**
> any listPrintersApiV1ExportPrintersGet()

List available printers.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPrintersApiV1ExportPrintersGet(
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

# **listPrintersApiV1ExportPrintersGet_0**
> any listPrintersApiV1ExportPrintersGet_0()

List available printers.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPrintersApiV1ExportPrintersGet_0(
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

# **printDocumentApiV1ExportDocumentIdPrintPost**
> any printDocumentApiV1ExportDocumentIdPrintPost(printRequest)

Print a document.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    PrintRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let printRequest: PrintRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.printDocumentApiV1ExportDocumentIdPrintPost(
    documentId,
    printRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **printRequest** | **PrintRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **printDocumentApiV1ExportDocumentIdPrintPost_0**
> any printDocumentApiV1ExportDocumentIdPrintPost_0(printRequest)

Print a document.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    PrintRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let printRequest: PrintRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.printDocumentApiV1ExportDocumentIdPrintPost_0(
    documentId,
    printRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **printRequest** | **PrintRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **publishToPortalApiV1ExportDistributionPortalDocumentIdPost**
> any publishToPortalApiV1ExportDistributionPortalDocumentIdPost(portalPublishRequest)

Publish document to portal.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    PortalPublishRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let portalPublishRequest: PortalPublishRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.publishToPortalApiV1ExportDistributionPortalDocumentIdPost(
    documentId,
    portalPublishRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **portalPublishRequest** | **PortalPublishRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **publishToPortalApiV1ExportDistributionPortalDocumentIdPost_0**
> any publishToPortalApiV1ExportDistributionPortalDocumentIdPost_0(portalPublishRequest)

Publish document to portal.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    PortalPublishRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let documentId: string; // (default to undefined)
let portalPublishRequest: PortalPublishRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.publishToPortalApiV1ExportDistributionPortalDocumentIdPost_0(
    documentId,
    portalPublishRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **portalPublishRequest** | **PortalPublishRequest**|  | |
| **documentId** | [**string**] |  | defaults to undefined|
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

# **revokeEmbedTokenApiV1ExportEmbedTokenIdDelete**
> any revokeEmbedTokenApiV1ExportEmbedTokenIdDelete()

Revoke an embed token.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let tokenId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.revokeEmbedTokenApiV1ExportEmbedTokenIdDelete(
    tokenId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tokenId** | [**string**] |  | defaults to undefined|
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

# **revokeEmbedTokenApiV1ExportEmbedTokenIdDelete_0**
> any revokeEmbedTokenApiV1ExportEmbedTokenIdDelete_0()

Revoke an embed token.

### Example

```typescript
import {
    ExportApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let tokenId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.revokeEmbedTokenApiV1ExportEmbedTokenIdDelete_0(
    tokenId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tokenId** | [**string**] |  | defaults to undefined|
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

# **sendToSlackApiV1ExportDistributionSlackPost**
> any sendToSlackApiV1ExportDistributionSlackPost(slackMessageRequest)

Send document to Slack channel.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    SlackMessageRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let slackMessageRequest: SlackMessageRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.sendToSlackApiV1ExportDistributionSlackPost(
    slackMessageRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **slackMessageRequest** | **SlackMessageRequest**|  | |
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

# **sendToSlackApiV1ExportDistributionSlackPost_0**
> any sendToSlackApiV1ExportDistributionSlackPost_0(slackMessageRequest)

Send document to Slack channel.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    SlackMessageRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let slackMessageRequest: SlackMessageRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.sendToSlackApiV1ExportDistributionSlackPost_0(
    slackMessageRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **slackMessageRequest** | **SlackMessageRequest**|  | |
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

# **sendToTeamsApiV1ExportDistributionTeamsPost**
> any sendToTeamsApiV1ExportDistributionTeamsPost(teamsMessageRequest)

Send document to Microsoft Teams.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    TeamsMessageRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let teamsMessageRequest: TeamsMessageRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.sendToTeamsApiV1ExportDistributionTeamsPost(
    teamsMessageRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamsMessageRequest** | **TeamsMessageRequest**|  | |
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

# **sendToTeamsApiV1ExportDistributionTeamsPost_0**
> any sendToTeamsApiV1ExportDistributionTeamsPost_0(teamsMessageRequest)

Send document to Microsoft Teams.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    TeamsMessageRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let teamsMessageRequest: TeamsMessageRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.sendToTeamsApiV1ExportDistributionTeamsPost_0(
    teamsMessageRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamsMessageRequest** | **TeamsMessageRequest**|  | |
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

# **sendWebhookApiV1ExportDistributionWebhookPost**
> any sendWebhookApiV1ExportDistributionWebhookPost(webhookDeliveryRequest)

Deliver document via webhook.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    WebhookDeliveryRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let webhookDeliveryRequest: WebhookDeliveryRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.sendWebhookApiV1ExportDistributionWebhookPost(
    webhookDeliveryRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookDeliveryRequest** | **WebhookDeliveryRequest**|  | |
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

# **sendWebhookApiV1ExportDistributionWebhookPost_0**
> any sendWebhookApiV1ExportDistributionWebhookPost_0(webhookDeliveryRequest)

Deliver document via webhook.

### Example

```typescript
import {
    ExportApi,
    Configuration,
    WebhookDeliveryRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportApi(configuration);

let webhookDeliveryRequest: WebhookDeliveryRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.sendWebhookApiV1ExportDistributionWebhookPost_0(
    webhookDeliveryRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **webhookDeliveryRequest** | **WebhookDeliveryRequest**|  | |
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

