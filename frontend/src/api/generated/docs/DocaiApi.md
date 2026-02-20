# DocaiApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**analyzeContractApiV1DocaiParseContractPost**](#analyzecontractapiv1docaiparsecontractpost) | **POST** /api/v1/docai/parse/contract | Analyze Contract|
|[**analyzeContractApiV1DocaiParseContractPost_0**](#analyzecontractapiv1docaiparsecontractpost_0) | **POST** /api/v1/docai/parse/contract | Analyze Contract|
|[**checkComplianceApiV1DocaiCompliancePost**](#checkcomplianceapiv1docaicompliancepost) | **POST** /api/v1/docai/compliance | Check Compliance|
|[**checkComplianceApiV1DocaiCompliancePost_0**](#checkcomplianceapiv1docaicompliancepost_0) | **POST** /api/v1/docai/compliance | Check Compliance|
|[**classifyDocumentApiV1DocaiClassifyPost**](#classifydocumentapiv1docaiclassifypost) | **POST** /api/v1/docai/classify | Classify Document|
|[**classifyDocumentApiV1DocaiClassifyPost_0**](#classifydocumentapiv1docaiclassifypost_0) | **POST** /api/v1/docai/classify | Classify Document|
|[**compareDocumentsApiV1DocaiComparePost**](#comparedocumentsapiv1docaicomparepost) | **POST** /api/v1/docai/compare | Compare Documents|
|[**compareDocumentsApiV1DocaiComparePost_0**](#comparedocumentsapiv1docaicomparepost_0) | **POST** /api/v1/docai/compare | Compare Documents|
|[**extractEntitiesApiV1DocaiEntitiesPost**](#extractentitiesapiv1docaientitiespost) | **POST** /api/v1/docai/entities | Extract Entities|
|[**extractEntitiesApiV1DocaiEntitiesPost_0**](#extractentitiesapiv1docaientitiespost_0) | **POST** /api/v1/docai/entities | Extract Entities|
|[**parseInvoiceApiV1DocaiParseInvoicePost**](#parseinvoiceapiv1docaiparseinvoicepost) | **POST** /api/v1/docai/parse/invoice | Parse Invoice|
|[**parseInvoiceApiV1DocaiParseInvoicePost_0**](#parseinvoiceapiv1docaiparseinvoicepost_0) | **POST** /api/v1/docai/parse/invoice | Parse Invoice|
|[**parseResumeApiV1DocaiParseResumePost**](#parseresumeapiv1docaiparseresumepost) | **POST** /api/v1/docai/parse/resume | Parse Resume|
|[**parseResumeApiV1DocaiParseResumePost_0**](#parseresumeapiv1docaiparseresumepost_0) | **POST** /api/v1/docai/parse/resume | Parse Resume|
|[**scanReceiptApiV1DocaiParseReceiptPost**](#scanreceiptapiv1docaiparsereceiptpost) | **POST** /api/v1/docai/parse/receipt | Scan Receipt|
|[**scanReceiptApiV1DocaiParseReceiptPost_0**](#scanreceiptapiv1docaiparsereceiptpost_0) | **POST** /api/v1/docai/parse/receipt | Scan Receipt|
|[**semanticSearchApiV1DocaiSearchPost**](#semanticsearchapiv1docaisearchpost) | **POST** /api/v1/docai/search | Semantic Search|
|[**semanticSearchApiV1DocaiSearchPost_0**](#semanticsearchapiv1docaisearchpost_0) | **POST** /api/v1/docai/search | Semantic Search|
|[**summarizeMultipleApiV1DocaiSummarizeMultiPost**](#summarizemultipleapiv1docaisummarizemultipost) | **POST** /api/v1/docai/summarize/multi | Summarize Multiple|
|[**summarizeMultipleApiV1DocaiSummarizeMultiPost_0**](#summarizemultipleapiv1docaisummarizemultipost_0) | **POST** /api/v1/docai/summarize/multi | Summarize Multiple|

# **analyzeContractApiV1DocaiParseContractPost**
> ContractAnalyzeResponse analyzeContractApiV1DocaiParseContractPost(contractAnalyzeRequest)

Analyze a contract document.  Extracts parties, clauses, obligations, key dates, and performs risk analysis on contract documents.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ContractAnalyzeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let contractAnalyzeRequest: ContractAnalyzeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.analyzeContractApiV1DocaiParseContractPost(
    contractAnalyzeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **contractAnalyzeRequest** | **ContractAnalyzeRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ContractAnalyzeResponse**

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

# **analyzeContractApiV1DocaiParseContractPost_0**
> ContractAnalyzeResponse analyzeContractApiV1DocaiParseContractPost_0(contractAnalyzeRequest)

Analyze a contract document.  Extracts parties, clauses, obligations, key dates, and performs risk analysis on contract documents.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ContractAnalyzeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let contractAnalyzeRequest: ContractAnalyzeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.analyzeContractApiV1DocaiParseContractPost_0(
    contractAnalyzeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **contractAnalyzeRequest** | **ContractAnalyzeRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ContractAnalyzeResponse**

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

# **checkComplianceApiV1DocaiCompliancePost**
> ComplianceCheckResponse checkComplianceApiV1DocaiCompliancePost(complianceCheckRequest)

Check document for regulatory compliance.  Analyzes document against specified regulations (GDPR, HIPAA, SOC2) and identifies violations and recommendations.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ComplianceCheckRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let complianceCheckRequest: ComplianceCheckRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkComplianceApiV1DocaiCompliancePost(
    complianceCheckRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **complianceCheckRequest** | **ComplianceCheckRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ComplianceCheckResponse**

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

# **checkComplianceApiV1DocaiCompliancePost_0**
> ComplianceCheckResponse checkComplianceApiV1DocaiCompliancePost_0(complianceCheckRequest)

Check document for regulatory compliance.  Analyzes document against specified regulations (GDPR, HIPAA, SOC2) and identifies violations and recommendations.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ComplianceCheckRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let complianceCheckRequest: ComplianceCheckRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkComplianceApiV1DocaiCompliancePost_0(
    complianceCheckRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **complianceCheckRequest** | **ComplianceCheckRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ComplianceCheckResponse**

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

# **classifyDocumentApiV1DocaiClassifyPost**
> ClassifyResponse classifyDocumentApiV1DocaiClassifyPost(classifyRequest)

Classify a document by type.  Determines document category (invoice, contract, resume, receipt, etc.) and suggests appropriate parsers for further processing.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ClassifyRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let classifyRequest: ClassifyRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.classifyDocumentApiV1DocaiClassifyPost(
    classifyRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **classifyRequest** | **ClassifyRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ClassifyResponse**

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

# **classifyDocumentApiV1DocaiClassifyPost_0**
> ClassifyResponse classifyDocumentApiV1DocaiClassifyPost_0(classifyRequest)

Classify a document by type.  Determines document category (invoice, contract, resume, receipt, etc.) and suggests appropriate parsers for further processing.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ClassifyRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let classifyRequest: ClassifyRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.classifyDocumentApiV1DocaiClassifyPost_0(
    classifyRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **classifyRequest** | **ClassifyRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ClassifyResponse**

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

# **compareDocumentsApiV1DocaiComparePost**
> CompareResponse compareDocumentsApiV1DocaiComparePost(backendAppSchemasDocaiSchemasCompareRequest)

Compare two documents.  Calculates similarity, identifies differences, and optionally performs semantic comparison to find meaningful changes.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    BackendAppSchemasDocaiSchemasCompareRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let backendAppSchemasDocaiSchemasCompareRequest: BackendAppSchemasDocaiSchemasCompareRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.compareDocumentsApiV1DocaiComparePost(
    backendAppSchemasDocaiSchemasCompareRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasDocaiSchemasCompareRequest** | **BackendAppSchemasDocaiSchemasCompareRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompareResponse**

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

# **compareDocumentsApiV1DocaiComparePost_0**
> CompareResponse compareDocumentsApiV1DocaiComparePost_0(backendAppSchemasDocaiSchemasCompareRequest)

Compare two documents.  Calculates similarity, identifies differences, and optionally performs semantic comparison to find meaningful changes.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    BackendAppSchemasDocaiSchemasCompareRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let backendAppSchemasDocaiSchemasCompareRequest: BackendAppSchemasDocaiSchemasCompareRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.compareDocumentsApiV1DocaiComparePost_0(
    backendAppSchemasDocaiSchemasCompareRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasDocaiSchemasCompareRequest** | **BackendAppSchemasDocaiSchemasCompareRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompareResponse**

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

# **extractEntitiesApiV1DocaiEntitiesPost**
> EntityExtractResponse extractEntitiesApiV1DocaiEntitiesPost(entityExtractRequest)

Extract named entities from a document.  Identifies and extracts entities like persons, organizations, locations, dates, monetary values, emails, phones, and URLs.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    EntityExtractRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let entityExtractRequest: EntityExtractRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.extractEntitiesApiV1DocaiEntitiesPost(
    entityExtractRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **entityExtractRequest** | **EntityExtractRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**EntityExtractResponse**

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

# **extractEntitiesApiV1DocaiEntitiesPost_0**
> EntityExtractResponse extractEntitiesApiV1DocaiEntitiesPost_0(entityExtractRequest)

Extract named entities from a document.  Identifies and extracts entities like persons, organizations, locations, dates, monetary values, emails, phones, and URLs.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    EntityExtractRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let entityExtractRequest: EntityExtractRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.extractEntitiesApiV1DocaiEntitiesPost_0(
    entityExtractRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **entityExtractRequest** | **EntityExtractRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**EntityExtractResponse**

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

# **parseInvoiceApiV1DocaiParseInvoicePost**
> InvoiceParseResponse parseInvoiceApiV1DocaiParseInvoicePost(invoiceParseRequest)

Parse an invoice document and extract structured data.  Extracts invoice number, dates, vendor/billing info, line items, and totals from invoice documents (PDF, images, or text).

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    InvoiceParseRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let invoiceParseRequest: InvoiceParseRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.parseInvoiceApiV1DocaiParseInvoicePost(
    invoiceParseRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **invoiceParseRequest** | **InvoiceParseRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**InvoiceParseResponse**

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

# **parseInvoiceApiV1DocaiParseInvoicePost_0**
> InvoiceParseResponse parseInvoiceApiV1DocaiParseInvoicePost_0(invoiceParseRequest)

Parse an invoice document and extract structured data.  Extracts invoice number, dates, vendor/billing info, line items, and totals from invoice documents (PDF, images, or text).

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    InvoiceParseRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let invoiceParseRequest: InvoiceParseRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.parseInvoiceApiV1DocaiParseInvoicePost_0(
    invoiceParseRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **invoiceParseRequest** | **InvoiceParseRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**InvoiceParseResponse**

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

# **parseResumeApiV1DocaiParseResumePost**
> ResumeParseResponse parseResumeApiV1DocaiParseResumePost(resumeParseRequest)

Parse a resume/CV document.  Extracts contact info, education, work experience, skills, certifications, and can optionally match against a job description.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ResumeParseRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let resumeParseRequest: ResumeParseRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.parseResumeApiV1DocaiParseResumePost(
    resumeParseRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **resumeParseRequest** | **ResumeParseRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ResumeParseResponse**

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

# **parseResumeApiV1DocaiParseResumePost_0**
> ResumeParseResponse parseResumeApiV1DocaiParseResumePost_0(resumeParseRequest)

Parse a resume/CV document.  Extracts contact info, education, work experience, skills, certifications, and can optionally match against a job description.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ResumeParseRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let resumeParseRequest: ResumeParseRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.parseResumeApiV1DocaiParseResumePost_0(
    resumeParseRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **resumeParseRequest** | **ResumeParseRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ResumeParseResponse**

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

# **scanReceiptApiV1DocaiParseReceiptPost**
> ReceiptScanResponse scanReceiptApiV1DocaiParseReceiptPost(receiptScanRequest)

Scan a receipt document.  Extracts merchant info, date/time, line items, totals, and payment information from receipt images or PDFs.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ReceiptScanRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let receiptScanRequest: ReceiptScanRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scanReceiptApiV1DocaiParseReceiptPost(
    receiptScanRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **receiptScanRequest** | **ReceiptScanRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ReceiptScanResponse**

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

# **scanReceiptApiV1DocaiParseReceiptPost_0**
> ReceiptScanResponse scanReceiptApiV1DocaiParseReceiptPost_0(receiptScanRequest)

Scan a receipt document.  Extracts merchant info, date/time, line items, totals, and payment information from receipt images or PDFs.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    ReceiptScanRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let receiptScanRequest: ReceiptScanRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scanReceiptApiV1DocaiParseReceiptPost_0(
    receiptScanRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **receiptScanRequest** | **ReceiptScanRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ReceiptScanResponse**

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

# **semanticSearchApiV1DocaiSearchPost**
> SemanticSearchResponse semanticSearchApiV1DocaiSearchPost(backendAppSchemasDocaiSchemasSemanticSearchRequest)

Perform semantic search across documents.  Uses embeddings to find semantically similar content rather than exact keyword matches.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    BackendAppSchemasDocaiSchemasSemanticSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let backendAppSchemasDocaiSchemasSemanticSearchRequest: BackendAppSchemasDocaiSchemasSemanticSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.semanticSearchApiV1DocaiSearchPost(
    backendAppSchemasDocaiSchemasSemanticSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasDocaiSchemasSemanticSearchRequest** | **BackendAppSchemasDocaiSchemasSemanticSearchRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SemanticSearchResponse**

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

# **semanticSearchApiV1DocaiSearchPost_0**
> SemanticSearchResponse semanticSearchApiV1DocaiSearchPost_0(backendAppSchemasDocaiSchemasSemanticSearchRequest)

Perform semantic search across documents.  Uses embeddings to find semantically similar content rather than exact keyword matches.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    BackendAppSchemasDocaiSchemasSemanticSearchRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let backendAppSchemasDocaiSchemasSemanticSearchRequest: BackendAppSchemasDocaiSchemasSemanticSearchRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.semanticSearchApiV1DocaiSearchPost_0(
    backendAppSchemasDocaiSchemasSemanticSearchRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **backendAppSchemasDocaiSchemasSemanticSearchRequest** | **BackendAppSchemasDocaiSchemasSemanticSearchRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SemanticSearchResponse**

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

# **summarizeMultipleApiV1DocaiSummarizeMultiPost**
> MultiDocSummarizeResponse summarizeMultipleApiV1DocaiSummarizeMultiPost(multiDocSummarizeRequest)

Summarize multiple documents.  Creates a unified summary across multiple documents, identifying key points and common themes with source references.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    MultiDocSummarizeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let multiDocSummarizeRequest: MultiDocSummarizeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.summarizeMultipleApiV1DocaiSummarizeMultiPost(
    multiDocSummarizeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **multiDocSummarizeRequest** | **MultiDocSummarizeRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MultiDocSummarizeResponse**

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

# **summarizeMultipleApiV1DocaiSummarizeMultiPost_0**
> MultiDocSummarizeResponse summarizeMultipleApiV1DocaiSummarizeMultiPost_0(multiDocSummarizeRequest)

Summarize multiple documents.  Creates a unified summary across multiple documents, identifying key points and common themes with source references.

### Example

```typescript
import {
    DocaiApi,
    Configuration,
    MultiDocSummarizeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new DocaiApi(configuration);

let multiDocSummarizeRequest: MultiDocSummarizeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.summarizeMultipleApiV1DocaiSummarizeMultiPost_0(
    multiDocSummarizeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **multiDocSummarizeRequest** | **MultiDocSummarizeRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MultiDocSummarizeResponse**

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

