# AiApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**analyzeDataQualityApiV1AiSpreadsheetsSpreadsheetIdCleanPost**](#analyzedataqualityapiv1aispreadsheetsspreadsheetidcleanpost) | **POST** /api/v1/ai/spreadsheets/{spreadsheet_id}/clean | Analyze Data Quality|
|[**checkAiHealthApiV1AiHealthGet**](#checkaihealthapiv1aihealthget) | **GET** /api/v1/ai/health | Check Ai Health|
|[**checkGrammarApiV1AiDocumentsDocumentIdAiGrammarPost**](#checkgrammarapiv1aidocumentsdocumentidaigrammarpost) | **POST** /api/v1/ai/documents/{document_id}/ai/grammar | Check Grammar|
|[**detectAnomaliesApiV1AiSpreadsheetsSpreadsheetIdAnomaliesPost**](#detectanomaliesapiv1aispreadsheetsspreadsheetidanomaliespost) | **POST** /api/v1/ai/spreadsheets/{spreadsheet_id}/anomalies | Detect Anomalies|
|[**expandTextApiV1AiDocumentsDocumentIdAiExpandPost**](#expandtextapiv1aidocumentsdocumentidaiexpandpost) | **POST** /api/v1/ai/documents/{document_id}/ai/expand | Expand Text|
|[**explainFormulaApiV1AiSpreadsheetsSpreadsheetIdExplainPost**](#explainformulaapiv1aispreadsheetsspreadsheetidexplainpost) | **POST** /api/v1/ai/spreadsheets/{spreadsheet_id}/explain | Explain Formula|
|[**generateContentApiV1AiAiGeneratePost**](#generatecontentapiv1aiaigeneratepost) | **POST** /api/v1/ai/ai/generate | Generate Content|
|[**generatePredictionsApiV1AiSpreadsheetsSpreadsheetIdPredictPost**](#generatepredictionsapiv1aispreadsheetsspreadsheetidpredictpost) | **POST** /api/v1/ai/spreadsheets/{spreadsheet_id}/predict | Generate Predictions|
|[**getAvailableTonesApiV1AiTonesGet**](#getavailabletonesapiv1aitonesget) | **GET** /api/v1/ai/tones | Get Available Tones|
|[**naturalLanguageToFormulaApiV1AiSpreadsheetsSpreadsheetIdFormulaPost**](#naturallanguagetoformulaapiv1aispreadsheetsspreadsheetidformulapost) | **POST** /api/v1/ai/spreadsheets/{spreadsheet_id}/formula | Natural Language To Formula|
|[**rewriteTextApiV1AiDocumentsDocumentIdAiRewritePost**](#rewritetextapiv1aidocumentsdocumentidairewritepost) | **POST** /api/v1/ai/documents/{document_id}/ai/rewrite | Rewrite Text|
|[**suggestFormulasApiV1AiSpreadsheetsSpreadsheetIdSuggestPost**](#suggestformulasapiv1aispreadsheetsspreadsheetidsuggestpost) | **POST** /api/v1/ai/spreadsheets/{spreadsheet_id}/suggest | Suggest Formulas|
|[**summarizeTextApiV1AiDocumentsDocumentIdAiSummarizePost**](#summarizetextapiv1aidocumentsdocumentidaisummarizepost) | **POST** /api/v1/ai/documents/{document_id}/ai/summarize | Summarize Text|
|[**translateTextApiV1AiDocumentsDocumentIdAiTranslatePost**](#translatetextapiv1aidocumentsdocumentidaitranslatepost) | **POST** /api/v1/ai/documents/{document_id}/ai/translate | Translate Text|

# **analyzeDataQualityApiV1AiSpreadsheetsSpreadsheetIdCleanPost**
> any analyzeDataQualityApiV1AiSpreadsheetsSpreadsheetIdCleanPost(dataQualityRequest)

Analyze data for quality issues and provide cleaning suggestions.  Returns:     DataCleaningResult with suggestions and quality score.

### Example

```typescript
import {
    AiApi,
    Configuration,
    DataQualityRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let spreadsheetId: string; // (default to undefined)
let dataQualityRequest: DataQualityRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.analyzeDataQualityApiV1AiSpreadsheetsSpreadsheetIdCleanPost(
    spreadsheetId,
    dataQualityRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dataQualityRequest** | **DataQualityRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **checkAiHealthApiV1AiHealthGet**
> any checkAiHealthApiV1AiHealthGet()

Check if AI services are configured and available.

### Example

```typescript
import {
    AiApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkAiHealthApiV1AiHealthGet(
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

# **checkGrammarApiV1AiDocumentsDocumentIdAiGrammarPost**
> any checkGrammarApiV1AiDocumentsDocumentIdAiGrammarPost(grammarCheckRequest)

Check text for grammar, spelling, and style issues.  Returns:     GrammarCheckResult with issues, corrected text, and quality score.  Status codes:     200: Success     400: Invalid input (text too long)     503: AI service temporarily unavailable

### Example

```typescript
import {
    AiApi,
    Configuration,
    GrammarCheckRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let documentId: string; // (default to undefined)
let grammarCheckRequest: GrammarCheckRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkGrammarApiV1AiDocumentsDocumentIdAiGrammarPost(
    documentId,
    grammarCheckRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **grammarCheckRequest** | **GrammarCheckRequest**|  | |
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

# **detectAnomaliesApiV1AiSpreadsheetsSpreadsheetIdAnomaliesPost**
> any detectAnomaliesApiV1AiSpreadsheetsSpreadsheetIdAnomaliesPost(anomalyRequest)

Detect anomalies in spreadsheet data.  Returns:     AnomalyDetectionResult with detected anomalies.

### Example

```typescript
import {
    AiApi,
    Configuration,
    AnomalyRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let spreadsheetId: string; // (default to undefined)
let anomalyRequest: AnomalyRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.detectAnomaliesApiV1AiSpreadsheetsSpreadsheetIdAnomaliesPost(
    spreadsheetId,
    anomalyRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **anomalyRequest** | **AnomalyRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **expandTextApiV1AiDocumentsDocumentIdAiExpandPost**
> any expandTextApiV1AiDocumentsDocumentIdAiExpandPost(expandRequest)

Expand text with additional details and examples.  Returns:     ExpandResult with expanded text and word counts.

### Example

```typescript
import {
    AiApi,
    Configuration,
    ExpandRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let documentId: string; // (default to undefined)
let expandRequest: ExpandRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.expandTextApiV1AiDocumentsDocumentIdAiExpandPost(
    documentId,
    expandRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **expandRequest** | **ExpandRequest**|  | |
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

# **explainFormulaApiV1AiSpreadsheetsSpreadsheetIdExplainPost**
> any explainFormulaApiV1AiSpreadsheetsSpreadsheetIdExplainPost(explainFormulaRequest)

Explain what a formula does in plain language.  Returns:     FormulaExplanation with detailed breakdown.

### Example

```typescript
import {
    AiApi,
    Configuration,
    ExplainFormulaRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let spreadsheetId: string; // (default to undefined)
let explainFormulaRequest: ExplainFormulaRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.explainFormulaApiV1AiSpreadsheetsSpreadsheetIdExplainPost(
    spreadsheetId,
    explainFormulaRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **explainFormulaRequest** | **ExplainFormulaRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **generateContentApiV1AiAiGeneratePost**
> any generateContentApiV1AiAiGeneratePost(generateContentRequest)

Generate new content based on a prompt.  Returns:     Generated content string.

### Example

```typescript
import {
    AiApi,
    Configuration,
    GenerateContentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let generateContentRequest: GenerateContentRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateContentApiV1AiAiGeneratePost(
    generateContentRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **generateContentRequest** | **GenerateContentRequest**|  | |
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

# **generatePredictionsApiV1AiSpreadsheetsSpreadsheetIdPredictPost**
> any generatePredictionsApiV1AiSpreadsheetsSpreadsheetIdPredictPost(predictionRequest)

Generate predictions for a new column based on existing data.  Returns:     PredictionColumn with predictions and confidence scores.

### Example

```typescript
import {
    AiApi,
    Configuration,
    PredictionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let spreadsheetId: string; // (default to undefined)
let predictionRequest: PredictionRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generatePredictionsApiV1AiSpreadsheetsSpreadsheetIdPredictPost(
    spreadsheetId,
    predictionRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **predictionRequest** | **PredictionRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **getAvailableTonesApiV1AiTonesGet**
> any getAvailableTonesApiV1AiTonesGet()

Get list of available writing tones.

### Example

```typescript
import {
    AiApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAvailableTonesApiV1AiTonesGet(
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

# **naturalLanguageToFormulaApiV1AiSpreadsheetsSpreadsheetIdFormulaPost**
> any naturalLanguageToFormulaApiV1AiSpreadsheetsSpreadsheetIdFormulaPost(formulaRequest)

Convert natural language description to spreadsheet formula.  Returns:     FormulaResult with formula, explanation, and alternatives.

### Example

```typescript
import {
    AiApi,
    Configuration,
    FormulaRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let spreadsheetId: string; // (default to undefined)
let formulaRequest: FormulaRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.naturalLanguageToFormulaApiV1AiSpreadsheetsSpreadsheetIdFormulaPost(
    spreadsheetId,
    formulaRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **formulaRequest** | **FormulaRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **rewriteTextApiV1AiDocumentsDocumentIdAiRewritePost**
> any rewriteTextApiV1AiDocumentsDocumentIdAiRewritePost(rewriteRequest)

Rewrite text with specified tone.  Returns:     RewriteResult with rewritten text and list of changes.

### Example

```typescript
import {
    AiApi,
    Configuration,
    RewriteRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let documentId: string; // (default to undefined)
let rewriteRequest: RewriteRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.rewriteTextApiV1AiDocumentsDocumentIdAiRewritePost(
    documentId,
    rewriteRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **rewriteRequest** | **RewriteRequest**|  | |
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

# **suggestFormulasApiV1AiSpreadsheetsSpreadsheetIdSuggestPost**
> any suggestFormulasApiV1AiSpreadsheetsSpreadsheetIdSuggestPost(suggestFormulasRequest)

Suggest useful formulas based on data structure.  Returns:     List of suggested formulas with explanations.

### Example

```typescript
import {
    AiApi,
    Configuration,
    SuggestFormulasRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let spreadsheetId: string; // (default to undefined)
let suggestFormulasRequest: SuggestFormulasRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestFormulasApiV1AiSpreadsheetsSpreadsheetIdSuggestPost(
    spreadsheetId,
    suggestFormulasRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestFormulasRequest** | **SuggestFormulasRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **summarizeTextApiV1AiDocumentsDocumentIdAiSummarizePost**
> any summarizeTextApiV1AiDocumentsDocumentIdAiSummarizePost(summarizeRequest)

Summarize text with optional length limit.  Returns:     SummarizeResult with summary, key points, and compression ratio.

### Example

```typescript
import {
    AiApi,
    Configuration,
    SummarizeRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let documentId: string; // (default to undefined)
let summarizeRequest: SummarizeRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.summarizeTextApiV1AiDocumentsDocumentIdAiSummarizePost(
    documentId,
    summarizeRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **summarizeRequest** | **SummarizeRequest**|  | |
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

# **translateTextApiV1AiDocumentsDocumentIdAiTranslatePost**
> any translateTextApiV1AiDocumentsDocumentIdAiTranslatePost(translateRequest)

Translate text to target language.  Returns:     TranslateResult with translated text and confidence score.

### Example

```typescript
import {
    AiApi,
    Configuration,
    TranslateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiApi(configuration);

let documentId: string; // (default to undefined)
let translateRequest: TranslateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.translateTextApiV1AiDocumentsDocumentIdAiTranslatePost(
    documentId,
    translateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **translateRequest** | **TranslateRequest**|  | |
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

