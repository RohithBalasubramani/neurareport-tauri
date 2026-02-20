# SpreadsheetsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatPost**](#addconditionalformatapiv1spreadsheetsspreadsheetidsheetssheetidconditionalformatpost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/conditional-format | Add Conditional Format|
|[**addConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatPost_0**](#addconditionalformatapiv1spreadsheetsspreadsheetidsheetssheetidconditionalformatpost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/conditional-format | Add Conditional Format|
|[**addDataValidationApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdValidationPost**](#adddatavalidationapiv1spreadsheetsspreadsheetidsheetssheetidvalidationpost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/validation | Add Data Validation|
|[**addDataValidationApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdValidationPost_0**](#adddatavalidationapiv1spreadsheetsspreadsheetidsheetssheetidvalidationpost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/validation | Add Data Validation|
|[**addSheetApiV1SpreadsheetsSpreadsheetIdSheetsPost**](#addsheetapiv1spreadsheetsspreadsheetidsheetspost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/sheets | Add Sheet|
|[**addSheetApiV1SpreadsheetsSpreadsheetIdSheetsPost_0**](#addsheetapiv1spreadsheetsspreadsheetidsheetspost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/sheets | Add Sheet|
|[**createPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPost**](#createpivottableapiv1spreadsheetsspreadsheetidpivotpost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/pivot | Create Pivot Table|
|[**createPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPost_0**](#createpivottableapiv1spreadsheetsspreadsheetidpivotpost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/pivot | Create Pivot Table|
|[**createSpreadsheetApiV1SpreadsheetsPost**](#createspreadsheetapiv1spreadsheetspost) | **POST** /api/v1/spreadsheets | Create Spreadsheet|
|[**createSpreadsheetApiV1SpreadsheetsPost_0**](#createspreadsheetapiv1spreadsheetspost_0) | **POST** /api/v1/spreadsheets | Create Spreadsheet|
|[**deletePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdDelete**](#deletepivottableapiv1spreadsheetsspreadsheetidpivotpivotiddelete) | **DELETE** /api/v1/spreadsheets/{spreadsheet_id}/pivot/{pivot_id} | Delete Pivot Table|
|[**deletePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdDelete_0**](#deletepivottableapiv1spreadsheetsspreadsheetidpivotpivotiddelete_0) | **DELETE** /api/v1/spreadsheets/{spreadsheet_id}/pivot/{pivot_id} | Delete Pivot Table|
|[**deleteSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdDelete**](#deletesheetapiv1spreadsheetsspreadsheetidsheetssheetiddelete) | **DELETE** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id} | Delete Sheet|
|[**deleteSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdDelete_0**](#deletesheetapiv1spreadsheetsspreadsheetidsheetssheetiddelete_0) | **DELETE** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id} | Delete Sheet|
|[**deleteSpreadsheetApiV1SpreadsheetsSpreadsheetIdDelete**](#deletespreadsheetapiv1spreadsheetsspreadsheetiddelete) | **DELETE** /api/v1/spreadsheets/{spreadsheet_id} | Delete Spreadsheet|
|[**deleteSpreadsheetApiV1SpreadsheetsSpreadsheetIdDelete_0**](#deletespreadsheetapiv1spreadsheetsspreadsheetiddelete_0) | **DELETE** /api/v1/spreadsheets/{spreadsheet_id} | Delete Spreadsheet|
|[**detectAnomaliesEndpointApiV1SpreadsheetsSpreadsheetIdAiAnomaliesPost**](#detectanomaliesendpointapiv1spreadsheetsspreadsheetidaianomaliespost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/anomalies | Detect Anomalies Endpoint|
|[**detectAnomaliesEndpointApiV1SpreadsheetsSpreadsheetIdAiAnomaliesPost_0**](#detectanomaliesendpointapiv1spreadsheetsspreadsheetidaianomaliespost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/anomalies | Detect Anomalies Endpoint|
|[**evaluateFormulaApiV1SpreadsheetsSpreadsheetIdEvaluatePost**](#evaluateformulaapiv1spreadsheetsspreadsheetidevaluatepost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/evaluate | Evaluate Formula|
|[**evaluateFormulaApiV1SpreadsheetsSpreadsheetIdEvaluatePost_0**](#evaluateformulaapiv1spreadsheetsspreadsheetidevaluatepost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/evaluate | Evaluate Formula|
|[**explainFormulaEndpointApiV1SpreadsheetsSpreadsheetIdAiExplainPost**](#explainformulaendpointapiv1spreadsheetsspreadsheetidaiexplainpost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/explain | Explain Formula Endpoint|
|[**explainFormulaEndpointApiV1SpreadsheetsSpreadsheetIdAiExplainPost_0**](#explainformulaendpointapiv1spreadsheetsspreadsheetidaiexplainpost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/explain | Explain Formula Endpoint|
|[**exportSpreadsheetApiV1SpreadsheetsSpreadsheetIdExportGet**](#exportspreadsheetapiv1spreadsheetsspreadsheetidexportget) | **GET** /api/v1/spreadsheets/{spreadsheet_id}/export | Export Spreadsheet|
|[**exportSpreadsheetApiV1SpreadsheetsSpreadsheetIdExportGet_0**](#exportspreadsheetapiv1spreadsheetsspreadsheetidexportget_0) | **GET** /api/v1/spreadsheets/{spreadsheet_id}/export | Export Spreadsheet|
|[**freezePanesApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdFreezePut**](#freezepanesapiv1spreadsheetsspreadsheetidsheetssheetidfreezeput) | **PUT** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/freeze | Freeze Panes|
|[**freezePanesApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdFreezePut_0**](#freezepanesapiv1spreadsheetsspreadsheetidsheetssheetidfreezeput_0) | **PUT** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/freeze | Freeze Panes|
|[**generateFormulaApiV1SpreadsheetsSpreadsheetIdAiFormulaPost**](#generateformulaapiv1spreadsheetsspreadsheetidaiformulapost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/formula | Generate Formula|
|[**generateFormulaApiV1SpreadsheetsSpreadsheetIdAiFormulaPost_0**](#generateformulaapiv1spreadsheetsspreadsheetidaiformulapost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/formula | Generate Formula|
|[**generatePredictionsApiV1SpreadsheetsSpreadsheetIdAiPredictPost**](#generatepredictionsapiv1spreadsheetsspreadsheetidaipredictpost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/predict | Generate Predictions|
|[**generatePredictionsApiV1SpreadsheetsSpreadsheetIdAiPredictPost_0**](#generatepredictionsapiv1spreadsheetsspreadsheetidaipredictpost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/predict | Generate Predictions|
|[**getCellRangeApiV1SpreadsheetsSpreadsheetIdCellsGet**](#getcellrangeapiv1spreadsheetsspreadsheetidcellsget) | **GET** /api/v1/spreadsheets/{spreadsheet_id}/cells | Get Cell Range|
|[**getCellRangeApiV1SpreadsheetsSpreadsheetIdCellsGet_0**](#getcellrangeapiv1spreadsheetsspreadsheetidcellsget_0) | **GET** /api/v1/spreadsheets/{spreadsheet_id}/cells | Get Cell Range|
|[**getCollaboratorsApiV1SpreadsheetsSpreadsheetIdCollaboratorsGet**](#getcollaboratorsapiv1spreadsheetsspreadsheetidcollaboratorsget) | **GET** /api/v1/spreadsheets/{spreadsheet_id}/collaborators | Get Collaborators|
|[**getCollaboratorsApiV1SpreadsheetsSpreadsheetIdCollaboratorsGet_0**](#getcollaboratorsapiv1spreadsheetsspreadsheetidcollaboratorsget_0) | **GET** /api/v1/spreadsheets/{spreadsheet_id}/collaborators | Get Collaborators|
|[**getSpreadsheetApiV1SpreadsheetsSpreadsheetIdGet**](#getspreadsheetapiv1spreadsheetsspreadsheetidget) | **GET** /api/v1/spreadsheets/{spreadsheet_id} | Get Spreadsheet|
|[**getSpreadsheetApiV1SpreadsheetsSpreadsheetIdGet_0**](#getspreadsheetapiv1spreadsheetsspreadsheetidget_0) | **GET** /api/v1/spreadsheets/{spreadsheet_id} | Get Spreadsheet|
|[**importSpreadsheetApiV1SpreadsheetsImportPost**](#importspreadsheetapiv1spreadsheetsimportpost) | **POST** /api/v1/spreadsheets/import | Import Spreadsheet|
|[**importSpreadsheetApiV1SpreadsheetsImportPost_0**](#importspreadsheetapiv1spreadsheetsimportpost_0) | **POST** /api/v1/spreadsheets/import | Import Spreadsheet|
|[**listFormulaFunctionsApiV1SpreadsheetsFormulaFunctionsGet**](#listformulafunctionsapiv1spreadsheetsformulafunctionsget) | **GET** /api/v1/spreadsheets/formula/functions | List Formula Functions|
|[**listFormulaFunctionsApiV1SpreadsheetsFormulaFunctionsGet_0**](#listformulafunctionsapiv1spreadsheetsformulafunctionsget_0) | **GET** /api/v1/spreadsheets/formula/functions | List Formula Functions|
|[**listSpreadsheetsApiV1SpreadsheetsGet**](#listspreadsheetsapiv1spreadsheetsget) | **GET** /api/v1/spreadsheets | List Spreadsheets|
|[**listSpreadsheetsApiV1SpreadsheetsGet_0**](#listspreadsheetsapiv1spreadsheetsget_0) | **GET** /api/v1/spreadsheets | List Spreadsheets|
|[**refreshPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdRefreshPost**](#refreshpivottableapiv1spreadsheetsspreadsheetidpivotpivotidrefreshpost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/pivot/{pivot_id}/refresh | Refresh Pivot Table|
|[**refreshPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdRefreshPost_0**](#refreshpivottableapiv1spreadsheetsspreadsheetidpivotpivotidrefreshpost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/pivot/{pivot_id}/refresh | Refresh Pivot Table|
|[**removeConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatsFormatIdDelete**](#removeconditionalformatapiv1spreadsheetsspreadsheetidsheetssheetidconditionalformatsformatiddelete) | **DELETE** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/conditional-formats/{format_id} | Remove Conditional Format|
|[**removeConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatsFormatIdDelete_0**](#removeconditionalformatapiv1spreadsheetsspreadsheetidsheetssheetidconditionalformatsformatiddelete_0) | **DELETE** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/conditional-formats/{format_id} | Remove Conditional Format|
|[**renameSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdRenamePut**](#renamesheetapiv1spreadsheetsspreadsheetidsheetssheetidrenameput) | **PUT** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/rename | Rename Sheet|
|[**renameSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdRenamePut_0**](#renamesheetapiv1spreadsheetsspreadsheetidsheetssheetidrenameput_0) | **PUT** /api/v1/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/rename | Rename Sheet|
|[**startCollaborationApiV1SpreadsheetsSpreadsheetIdCollaboratePost**](#startcollaborationapiv1spreadsheetsspreadsheetidcollaboratepost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/collaborate | Start Collaboration|
|[**startCollaborationApiV1SpreadsheetsSpreadsheetIdCollaboratePost_0**](#startcollaborationapiv1spreadsheetsspreadsheetidcollaboratepost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/collaborate | Start Collaboration|
|[**suggestDataCleaningApiV1SpreadsheetsSpreadsheetIdAiCleanPost**](#suggestdatacleaningapiv1spreadsheetsspreadsheetidaicleanpost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/clean | Suggest Data Cleaning|
|[**suggestDataCleaningApiV1SpreadsheetsSpreadsheetIdAiCleanPost_0**](#suggestdatacleaningapiv1spreadsheetsspreadsheetidaicleanpost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/clean | Suggest Data Cleaning|
|[**suggestFormulasEndpointApiV1SpreadsheetsSpreadsheetIdAiSuggestPost**](#suggestformulasendpointapiv1spreadsheetsspreadsheetidaisuggestpost) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/suggest | Suggest Formulas Endpoint|
|[**suggestFormulasEndpointApiV1SpreadsheetsSpreadsheetIdAiSuggestPost_0**](#suggestformulasendpointapiv1spreadsheetsspreadsheetidaisuggestpost_0) | **POST** /api/v1/spreadsheets/{spreadsheet_id}/ai/suggest | Suggest Formulas Endpoint|
|[**updateCellsApiV1SpreadsheetsSpreadsheetIdCellsPut**](#updatecellsapiv1spreadsheetsspreadsheetidcellsput) | **PUT** /api/v1/spreadsheets/{spreadsheet_id}/cells | Update Cells|
|[**updateCellsApiV1SpreadsheetsSpreadsheetIdCellsPut_0**](#updatecellsapiv1spreadsheetsspreadsheetidcellsput_0) | **PUT** /api/v1/spreadsheets/{spreadsheet_id}/cells | Update Cells|
|[**updatePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdPut**](#updatepivottableapiv1spreadsheetsspreadsheetidpivotpivotidput) | **PUT** /api/v1/spreadsheets/{spreadsheet_id}/pivot/{pivot_id} | Update Pivot Table|
|[**updatePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdPut_0**](#updatepivottableapiv1spreadsheetsspreadsheetidpivotpivotidput_0) | **PUT** /api/v1/spreadsheets/{spreadsheet_id}/pivot/{pivot_id} | Update Pivot Table|
|[**updateSpreadsheetApiV1SpreadsheetsSpreadsheetIdPut**](#updatespreadsheetapiv1spreadsheetsspreadsheetidput) | **PUT** /api/v1/spreadsheets/{spreadsheet_id} | Update Spreadsheet|
|[**updateSpreadsheetApiV1SpreadsheetsSpreadsheetIdPut_0**](#updatespreadsheetapiv1spreadsheetsspreadsheetidput_0) | **PUT** /api/v1/spreadsheets/{spreadsheet_id} | Update Spreadsheet|
|[**validateFormulaApiV1SpreadsheetsFormulaValidatePost**](#validateformulaapiv1spreadsheetsformulavalidatepost) | **POST** /api/v1/spreadsheets/formula/validate | Validate Formula|
|[**validateFormulaApiV1SpreadsheetsFormulaValidatePost_0**](#validateformulaapiv1spreadsheetsformulavalidatepost_0) | **POST** /api/v1/spreadsheets/formula/validate | Validate Formula|

# **addConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatPost**
> any addConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatPost(conditionalFormatRequest)

Add conditional formatting rules.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    ConditionalFormatRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let conditionalFormatRequest: ConditionalFormatRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatPost(
    spreadsheetId,
    sheetId,
    conditionalFormatRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conditionalFormatRequest** | **ConditionalFormatRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
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

# **addConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatPost_0**
> any addConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatPost_0(conditionalFormatRequest)

Add conditional formatting rules.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    ConditionalFormatRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let conditionalFormatRequest: ConditionalFormatRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatPost_0(
    spreadsheetId,
    sheetId,
    conditionalFormatRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conditionalFormatRequest** | **ConditionalFormatRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
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

# **addDataValidationApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdValidationPost**
> any addDataValidationApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdValidationPost(dataValidationRequest)

Add data validation rules.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    DataValidationRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let dataValidationRequest: DataValidationRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDataValidationApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdValidationPost(
    spreadsheetId,
    sheetId,
    dataValidationRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dataValidationRequest** | **DataValidationRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
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

# **addDataValidationApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdValidationPost_0**
> any addDataValidationApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdValidationPost_0(dataValidationRequest)

Add data validation rules.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    DataValidationRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let dataValidationRequest: DataValidationRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addDataValidationApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdValidationPost_0(
    spreadsheetId,
    sheetId,
    dataValidationRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dataValidationRequest** | **DataValidationRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
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

# **addSheetApiV1SpreadsheetsSpreadsheetIdSheetsPost**
> SheetResponse addSheetApiV1SpreadsheetsSpreadsheetIdSheetsPost(addSheetRequest)

Add a new sheet to the spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    AddSheetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let addSheetRequest: AddSheetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addSheetApiV1SpreadsheetsSpreadsheetIdSheetsPost(
    spreadsheetId,
    addSheetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **addSheetRequest** | **AddSheetRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SheetResponse**

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

# **addSheetApiV1SpreadsheetsSpreadsheetIdSheetsPost_0**
> SheetResponse addSheetApiV1SpreadsheetsSpreadsheetIdSheetsPost_0(addSheetRequest)

Add a new sheet to the spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    AddSheetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let addSheetRequest: AddSheetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addSheetApiV1SpreadsheetsSpreadsheetIdSheetsPost_0(
    spreadsheetId,
    addSheetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **addSheetRequest** | **AddSheetRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SheetResponse**

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

# **createPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPost**
> PivotTableResponse createPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPost(pivotTableRequest)

Create a pivot table from spreadsheet data.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    PivotTableRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let pivotTableRequest: PivotTableRequest; //
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPost(
    spreadsheetId,
    pivotTableRequest,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pivotTableRequest** | **PivotTableRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PivotTableResponse**

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

# **createPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPost_0**
> PivotTableResponse createPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPost_0(pivotTableRequest)

Create a pivot table from spreadsheet data.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    PivotTableRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let pivotTableRequest: PivotTableRequest; //
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPost_0(
    spreadsheetId,
    pivotTableRequest,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pivotTableRequest** | **PivotTableRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PivotTableResponse**

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

# **createSpreadsheetApiV1SpreadsheetsPost**
> SpreadsheetResponse createSpreadsheetApiV1SpreadsheetsPost(createSpreadsheetRequest)

Create a new spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    CreateSpreadsheetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let createSpreadsheetRequest: CreateSpreadsheetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSpreadsheetApiV1SpreadsheetsPost(
    createSpreadsheetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createSpreadsheetRequest** | **CreateSpreadsheetRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SpreadsheetResponse**

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

# **createSpreadsheetApiV1SpreadsheetsPost_0**
> SpreadsheetResponse createSpreadsheetApiV1SpreadsheetsPost_0(createSpreadsheetRequest)

Create a new spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    CreateSpreadsheetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let createSpreadsheetRequest: CreateSpreadsheetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSpreadsheetApiV1SpreadsheetsPost_0(
    createSpreadsheetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createSpreadsheetRequest** | **CreateSpreadsheetRequest**|  | |
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SpreadsheetResponse**

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

# **deletePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdDelete**
> any deletePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdDelete()

Delete a pivot table.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let pivotId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdDelete(
    spreadsheetId,
    pivotId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **pivotId** | [**string**] |  | defaults to undefined|
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

# **deletePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdDelete_0**
> any deletePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdDelete_0()

Delete a pivot table.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let pivotId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdDelete_0(
    spreadsheetId,
    pivotId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **pivotId** | [**string**] |  | defaults to undefined|
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

# **deleteSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdDelete**
> any deleteSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdDelete()

Delete a sheet from the spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdDelete(
    spreadsheetId,
    sheetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
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

# **deleteSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdDelete_0**
> any deleteSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdDelete_0()

Delete a sheet from the spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdDelete_0(
    spreadsheetId,
    sheetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
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

# **deleteSpreadsheetApiV1SpreadsheetsSpreadsheetIdDelete**
> any deleteSpreadsheetApiV1SpreadsheetsSpreadsheetIdDelete()

Delete a spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSpreadsheetApiV1SpreadsheetsSpreadsheetIdDelete(
    spreadsheetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **deleteSpreadsheetApiV1SpreadsheetsSpreadsheetIdDelete_0**
> any deleteSpreadsheetApiV1SpreadsheetsSpreadsheetIdDelete_0()

Delete a spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSpreadsheetApiV1SpreadsheetsSpreadsheetIdDelete_0(
    spreadsheetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **detectAnomaliesEndpointApiV1SpreadsheetsSpreadsheetIdAiAnomaliesPost**
> any detectAnomaliesEndpointApiV1SpreadsheetsSpreadsheetIdAiAnomaliesPost()

Detect anomalies in a column.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let column: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let sensitivity: string; // (optional) (default to 'medium')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.detectAnomaliesEndpointApiV1SpreadsheetsSpreadsheetIdAiAnomaliesPost(
    spreadsheetId,
    column,
    sheetIndex,
    sensitivity,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **column** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **sensitivity** | [**string**] |  | (optional) defaults to 'medium'|
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

# **detectAnomaliesEndpointApiV1SpreadsheetsSpreadsheetIdAiAnomaliesPost_0**
> any detectAnomaliesEndpointApiV1SpreadsheetsSpreadsheetIdAiAnomaliesPost_0()

Detect anomalies in a column.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let column: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let sensitivity: string; // (optional) (default to 'medium')
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.detectAnomaliesEndpointApiV1SpreadsheetsSpreadsheetIdAiAnomaliesPost_0(
    spreadsheetId,
    column,
    sheetIndex,
    sensitivity,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **column** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **sensitivity** | [**string**] |  | (optional) defaults to 'medium'|
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

# **evaluateFormulaApiV1SpreadsheetsSpreadsheetIdEvaluatePost**
> any evaluateFormulaApiV1SpreadsheetsSpreadsheetIdEvaluatePost()

Evaluate a formula against spreadsheet data.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let formula: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.evaluateFormulaApiV1SpreadsheetsSpreadsheetIdEvaluatePost(
    spreadsheetId,
    formula,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **formula** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **evaluateFormulaApiV1SpreadsheetsSpreadsheetIdEvaluatePost_0**
> any evaluateFormulaApiV1SpreadsheetsSpreadsheetIdEvaluatePost_0()

Evaluate a formula against spreadsheet data.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let formula: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.evaluateFormulaApiV1SpreadsheetsSpreadsheetIdEvaluatePost_0(
    spreadsheetId,
    formula,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **formula** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **explainFormulaEndpointApiV1SpreadsheetsSpreadsheetIdAiExplainPost**
> any explainFormulaEndpointApiV1SpreadsheetsSpreadsheetIdAiExplainPost()

Explain what a formula does in plain language.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let formula: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.explainFormulaEndpointApiV1SpreadsheetsSpreadsheetIdAiExplainPost(
    spreadsheetId,
    formula,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **formula** | [**string**] |  | defaults to undefined|
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

# **explainFormulaEndpointApiV1SpreadsheetsSpreadsheetIdAiExplainPost_0**
> any explainFormulaEndpointApiV1SpreadsheetsSpreadsheetIdAiExplainPost_0()

Explain what a formula does in plain language.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let formula: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.explainFormulaEndpointApiV1SpreadsheetsSpreadsheetIdAiExplainPost_0(
    spreadsheetId,
    formula,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **formula** | [**string**] |  | defaults to undefined|
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

# **exportSpreadsheetApiV1SpreadsheetsSpreadsheetIdExportGet**
> any exportSpreadsheetApiV1SpreadsheetsSpreadsheetIdExportGet()

Export a spreadsheet to CSV or Excel format.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let format: string; // (optional) (default to 'csv')
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportSpreadsheetApiV1SpreadsheetsSpreadsheetIdExportGet(
    spreadsheetId,
    format,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **format** | [**string**] |  | (optional) defaults to 'csv'|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **exportSpreadsheetApiV1SpreadsheetsSpreadsheetIdExportGet_0**
> any exportSpreadsheetApiV1SpreadsheetsSpreadsheetIdExportGet_0()

Export a spreadsheet to CSV or Excel format.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let format: string; // (optional) (default to 'csv')
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportSpreadsheetApiV1SpreadsheetsSpreadsheetIdExportGet_0(
    spreadsheetId,
    format,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **format** | [**string**] |  | (optional) defaults to 'csv'|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **freezePanesApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdFreezePut**
> any freezePanesApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdFreezePut(freezePanesRequest)

Set frozen rows and columns.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    FreezePanesRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let freezePanesRequest: FreezePanesRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.freezePanesApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdFreezePut(
    spreadsheetId,
    sheetId,
    freezePanesRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **freezePanesRequest** | **FreezePanesRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
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

# **freezePanesApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdFreezePut_0**
> any freezePanesApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdFreezePut_0(freezePanesRequest)

Set frozen rows and columns.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    FreezePanesRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let freezePanesRequest: FreezePanesRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.freezePanesApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdFreezePut_0(
    spreadsheetId,
    sheetId,
    freezePanesRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **freezePanesRequest** | **FreezePanesRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
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

# **generateFormulaApiV1SpreadsheetsSpreadsheetIdAiFormulaPost**
> AIFormulaResponse generateFormulaApiV1SpreadsheetsSpreadsheetIdAiFormulaPost(aIFormulaRequest)

Generate a formula from natural language description.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    AIFormulaRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let aIFormulaRequest: AIFormulaRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateFormulaApiV1SpreadsheetsSpreadsheetIdAiFormulaPost(
    spreadsheetId,
    aIFormulaRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIFormulaRequest** | **AIFormulaRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIFormulaResponse**

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

# **generateFormulaApiV1SpreadsheetsSpreadsheetIdAiFormulaPost_0**
> AIFormulaResponse generateFormulaApiV1SpreadsheetsSpreadsheetIdAiFormulaPost_0(aIFormulaRequest)

Generate a formula from natural language description.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    AIFormulaRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let aIFormulaRequest: AIFormulaRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateFormulaApiV1SpreadsheetsSpreadsheetIdAiFormulaPost_0(
    spreadsheetId,
    aIFormulaRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIFormulaRequest** | **AIFormulaRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIFormulaResponse**

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

# **generatePredictionsApiV1SpreadsheetsSpreadsheetIdAiPredictPost**
> any generatePredictionsApiV1SpreadsheetsSpreadsheetIdAiPredictPost()

Generate predictive column based on existing data patterns.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let targetDescription: string; // (default to undefined)
let basedOnColumns: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generatePredictionsApiV1SpreadsheetsSpreadsheetIdAiPredictPost(
    spreadsheetId,
    targetDescription,
    basedOnColumns,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **targetDescription** | [**string**] |  | defaults to undefined|
| **basedOnColumns** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **generatePredictionsApiV1SpreadsheetsSpreadsheetIdAiPredictPost_0**
> any generatePredictionsApiV1SpreadsheetsSpreadsheetIdAiPredictPost_0()

Generate predictive column based on existing data patterns.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let targetDescription: string; // (default to undefined)
let basedOnColumns: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generatePredictionsApiV1SpreadsheetsSpreadsheetIdAiPredictPost_0(
    spreadsheetId,
    targetDescription,
    basedOnColumns,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **targetDescription** | [**string**] |  | defaults to undefined|
| **basedOnColumns** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **getCellRangeApiV1SpreadsheetsSpreadsheetIdCellsGet**
> any getCellRangeApiV1SpreadsheetsSpreadsheetIdCellsGet()

Get cell range from a spreadsheet sheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let startRow: number; // (optional) (default to 0)
let startCol: number; // (optional) (default to 0)
let endRow: number; // (optional) (default to 99)
let endCol: number; // (optional) (default to 25)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCellRangeApiV1SpreadsheetsSpreadsheetIdCellsGet(
    spreadsheetId,
    sheetIndex,
    startRow,
    startCol,
    endRow,
    endCol,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **startRow** | [**number**] |  | (optional) defaults to 0|
| **startCol** | [**number**] |  | (optional) defaults to 0|
| **endRow** | [**number**] |  | (optional) defaults to 99|
| **endCol** | [**number**] |  | (optional) defaults to 25|
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

# **getCellRangeApiV1SpreadsheetsSpreadsheetIdCellsGet_0**
> any getCellRangeApiV1SpreadsheetsSpreadsheetIdCellsGet_0()

Get cell range from a spreadsheet sheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let startRow: number; // (optional) (default to 0)
let startCol: number; // (optional) (default to 0)
let endRow: number; // (optional) (default to 99)
let endCol: number; // (optional) (default to 25)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCellRangeApiV1SpreadsheetsSpreadsheetIdCellsGet_0(
    spreadsheetId,
    sheetIndex,
    startRow,
    startCol,
    endRow,
    endCol,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **startRow** | [**number**] |  | (optional) defaults to 0|
| **startCol** | [**number**] |  | (optional) defaults to 0|
| **endRow** | [**number**] |  | (optional) defaults to 99|
| **endCol** | [**number**] |  | (optional) defaults to 25|
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

# **getCollaboratorsApiV1SpreadsheetsSpreadsheetIdCollaboratorsGet**
> any getCollaboratorsApiV1SpreadsheetsSpreadsheetIdCollaboratorsGet()

Get current collaborators for a spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCollaboratorsApiV1SpreadsheetsSpreadsheetIdCollaboratorsGet(
    spreadsheetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **getCollaboratorsApiV1SpreadsheetsSpreadsheetIdCollaboratorsGet_0**
> any getCollaboratorsApiV1SpreadsheetsSpreadsheetIdCollaboratorsGet_0()

Get current collaborators for a spreadsheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCollaboratorsApiV1SpreadsheetsSpreadsheetIdCollaboratorsGet_0(
    spreadsheetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **getSpreadsheetApiV1SpreadsheetsSpreadsheetIdGet**
> any getSpreadsheetApiV1SpreadsheetsSpreadsheetIdGet()

Get a spreadsheet with data.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSpreadsheetApiV1SpreadsheetsSpreadsheetIdGet(
    spreadsheetId,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **getSpreadsheetApiV1SpreadsheetsSpreadsheetIdGet_0**
> any getSpreadsheetApiV1SpreadsheetsSpreadsheetIdGet_0()

Get a spreadsheet with data.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSpreadsheetApiV1SpreadsheetsSpreadsheetIdGet_0(
    spreadsheetId,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **importSpreadsheetApiV1SpreadsheetsImportPost**
> any importSpreadsheetApiV1SpreadsheetsImportPost()

Import a spreadsheet from CSV or Excel file.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let file: File; // (default to undefined)
let name: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.importSpreadsheetApiV1SpreadsheetsImportPost(
    file,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **name** | [**string**] |  | (optional) defaults to undefined|
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

# **importSpreadsheetApiV1SpreadsheetsImportPost_0**
> any importSpreadsheetApiV1SpreadsheetsImportPost_0()

Import a spreadsheet from CSV or Excel file.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let file: File; // (default to undefined)
let name: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.importSpreadsheetApiV1SpreadsheetsImportPost_0(
    file,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **name** | [**string**] |  | (optional) defaults to undefined|
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

# **listFormulaFunctionsApiV1SpreadsheetsFormulaFunctionsGet**
> any listFormulaFunctionsApiV1SpreadsheetsFormulaFunctionsGet()

List available formula functions.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listFormulaFunctionsApiV1SpreadsheetsFormulaFunctionsGet(
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

# **listFormulaFunctionsApiV1SpreadsheetsFormulaFunctionsGet_0**
> any listFormulaFunctionsApiV1SpreadsheetsFormulaFunctionsGet_0()

List available formula functions.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listFormulaFunctionsApiV1SpreadsheetsFormulaFunctionsGet_0(
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

# **listSpreadsheetsApiV1SpreadsheetsGet**
> SpreadsheetListResponse listSpreadsheetsApiV1SpreadsheetsGet()

List all spreadsheets.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSpreadsheetsApiV1SpreadsheetsGet(
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SpreadsheetListResponse**

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

# **listSpreadsheetsApiV1SpreadsheetsGet_0**
> SpreadsheetListResponse listSpreadsheetsApiV1SpreadsheetsGet_0()

List all spreadsheets.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let limit: number; // (optional) (default to 100)
let offset: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSpreadsheetsApiV1SpreadsheetsGet_0(
    limit,
    offset,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SpreadsheetListResponse**

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

# **refreshPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdRefreshPost**
> PivotTableResponse refreshPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdRefreshPost()

Refresh/recompute a pivot table using its existing config.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let pivotId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdRefreshPost(
    spreadsheetId,
    pivotId,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **pivotId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PivotTableResponse**

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

# **refreshPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdRefreshPost_0**
> PivotTableResponse refreshPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdRefreshPost_0()

Refresh/recompute a pivot table using its existing config.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let pivotId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshPivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdRefreshPost_0(
    spreadsheetId,
    pivotId,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **pivotId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PivotTableResponse**

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

# **removeConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatsFormatIdDelete**
> any removeConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatsFormatIdDelete()

Remove a conditional format by ID from a sheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let formatId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatsFormatIdDelete(
    spreadsheetId,
    sheetId,
    formatId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
| **formatId** | [**string**] |  | defaults to undefined|
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

# **removeConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatsFormatIdDelete_0**
> any removeConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatsFormatIdDelete_0()

Remove a conditional format by ID from a sheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let formatId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeConditionalFormatApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdConditionalFormatsFormatIdDelete_0(
    spreadsheetId,
    sheetId,
    formatId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
| **formatId** | [**string**] |  | defaults to undefined|
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

# **renameSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdRenamePut**
> any renameSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdRenamePut()

Rename a sheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let name: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.renameSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdRenamePut(
    spreadsheetId,
    sheetId,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
| **name** | [**string**] |  | defaults to undefined|
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

# **renameSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdRenamePut_0**
> any renameSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdRenamePut_0()

Rename a sheet.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetId: string; // (default to undefined)
let name: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.renameSheetApiV1SpreadsheetsSpreadsheetIdSheetsSheetIdRenamePut_0(
    spreadsheetId,
    sheetId,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetId** | [**string**] |  | defaults to undefined|
| **name** | [**string**] |  | defaults to undefined|
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

# **startCollaborationApiV1SpreadsheetsSpreadsheetIdCollaboratePost**
> any startCollaborationApiV1SpreadsheetsSpreadsheetIdCollaboratePost()

Start a spreadsheet collaboration session.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.startCollaborationApiV1SpreadsheetsSpreadsheetIdCollaboratePost(
    spreadsheetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **startCollaborationApiV1SpreadsheetsSpreadsheetIdCollaboratePost_0**
> any startCollaborationApiV1SpreadsheetsSpreadsheetIdCollaboratePost_0()

Start a spreadsheet collaboration session.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.startCollaborationApiV1SpreadsheetsSpreadsheetIdCollaboratePost_0(
    spreadsheetId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
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

# **suggestDataCleaningApiV1SpreadsheetsSpreadsheetIdAiCleanPost**
> any suggestDataCleaningApiV1SpreadsheetsSpreadsheetIdAiCleanPost()

Get AI suggestions for cleaning data.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let column: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestDataCleaningApiV1SpreadsheetsSpreadsheetIdAiCleanPost(
    spreadsheetId,
    sheetIndex,
    column,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **column** | [**string**] |  | (optional) defaults to undefined|
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

# **suggestDataCleaningApiV1SpreadsheetsSpreadsheetIdAiCleanPost_0**
> any suggestDataCleaningApiV1SpreadsheetsSpreadsheetIdAiCleanPost_0()

Get AI suggestions for cleaning data.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let column: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestDataCleaningApiV1SpreadsheetsSpreadsheetIdAiCleanPost_0(
    spreadsheetId,
    sheetIndex,
    column,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **column** | [**string**] |  | (optional) defaults to undefined|
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

# **suggestFormulasEndpointApiV1SpreadsheetsSpreadsheetIdAiSuggestPost**
> any suggestFormulasEndpointApiV1SpreadsheetsSpreadsheetIdAiSuggestPost()

Get AI-suggested formulas based on data structure.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let analysisGoals: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestFormulasEndpointApiV1SpreadsheetsSpreadsheetIdAiSuggestPost(
    spreadsheetId,
    sheetIndex,
    analysisGoals,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **analysisGoals** | [**string**] |  | (optional) defaults to undefined|
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

# **suggestFormulasEndpointApiV1SpreadsheetsSpreadsheetIdAiSuggestPost_0**
> any suggestFormulasEndpointApiV1SpreadsheetsSpreadsheetIdAiSuggestPost_0()

Get AI-suggested formulas based on data structure.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let sheetIndex: number; // (optional) (default to 0)
let analysisGoals: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestFormulasEndpointApiV1SpreadsheetsSpreadsheetIdAiSuggestPost_0(
    spreadsheetId,
    sheetIndex,
    analysisGoals,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **analysisGoals** | [**string**] |  | (optional) defaults to undefined|
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

# **updateCellsApiV1SpreadsheetsSpreadsheetIdCellsPut**
> any updateCellsApiV1SpreadsheetsSpreadsheetIdCellsPut(cellUpdateRequest)

Update cell values.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    CellUpdateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let cellUpdateRequest: CellUpdateRequest; //
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCellsApiV1SpreadsheetsSpreadsheetIdCellsPut(
    spreadsheetId,
    cellUpdateRequest,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **cellUpdateRequest** | **CellUpdateRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **updateCellsApiV1SpreadsheetsSpreadsheetIdCellsPut_0**
> any updateCellsApiV1SpreadsheetsSpreadsheetIdCellsPut_0(cellUpdateRequest)

Update cell values.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    CellUpdateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let cellUpdateRequest: CellUpdateRequest; //
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCellsApiV1SpreadsheetsSpreadsheetIdCellsPut_0(
    spreadsheetId,
    cellUpdateRequest,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **cellUpdateRequest** | **CellUpdateRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
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

# **updatePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdPut**
> PivotTableResponse updatePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdPut(pivotTableRequest)

Update a pivot table and recompute with updated config.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    PivotTableRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let pivotId: string; // (default to undefined)
let pivotTableRequest: PivotTableRequest; //
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdPut(
    spreadsheetId,
    pivotId,
    pivotTableRequest,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pivotTableRequest** | **PivotTableRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **pivotId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PivotTableResponse**

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

# **updatePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdPut_0**
> PivotTableResponse updatePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdPut_0(pivotTableRequest)

Update a pivot table and recompute with updated config.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    PivotTableRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let pivotId: string; // (default to undefined)
let pivotTableRequest: PivotTableRequest; //
let sheetIndex: number; // (optional) (default to 0)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePivotTableApiV1SpreadsheetsSpreadsheetIdPivotPivotIdPut_0(
    spreadsheetId,
    pivotId,
    pivotTableRequest,
    sheetIndex,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pivotTableRequest** | **PivotTableRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **pivotId** | [**string**] |  | defaults to undefined|
| **sheetIndex** | [**number**] |  | (optional) defaults to 0|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PivotTableResponse**

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

# **updateSpreadsheetApiV1SpreadsheetsSpreadsheetIdPut**
> SpreadsheetResponse updateSpreadsheetApiV1SpreadsheetsSpreadsheetIdPut(updateSpreadsheetRequest)

Update spreadsheet metadata.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    UpdateSpreadsheetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let updateSpreadsheetRequest: UpdateSpreadsheetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSpreadsheetApiV1SpreadsheetsSpreadsheetIdPut(
    spreadsheetId,
    updateSpreadsheetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateSpreadsheetRequest** | **UpdateSpreadsheetRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SpreadsheetResponse**

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

# **updateSpreadsheetApiV1SpreadsheetsSpreadsheetIdPut_0**
> SpreadsheetResponse updateSpreadsheetApiV1SpreadsheetsSpreadsheetIdPut_0(updateSpreadsheetRequest)

Update spreadsheet metadata.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    UpdateSpreadsheetRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let spreadsheetId: string; // (default to undefined)
let updateSpreadsheetRequest: UpdateSpreadsheetRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSpreadsheetApiV1SpreadsheetsSpreadsheetIdPut_0(
    spreadsheetId,
    updateSpreadsheetRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **updateSpreadsheetRequest** | **UpdateSpreadsheetRequest**|  | |
| **spreadsheetId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SpreadsheetResponse**

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

# **validateFormulaApiV1SpreadsheetsFormulaValidatePost**
> any validateFormulaApiV1SpreadsheetsFormulaValidatePost(formulaValidateRequest)

Validate a formula syntax.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    FormulaValidateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let formulaValidateRequest: FormulaValidateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.validateFormulaApiV1SpreadsheetsFormulaValidatePost(
    formulaValidateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **formulaValidateRequest** | **FormulaValidateRequest**|  | |
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

# **validateFormulaApiV1SpreadsheetsFormulaValidatePost_0**
> any validateFormulaApiV1SpreadsheetsFormulaValidatePost_0(formulaValidateRequest)

Validate a formula syntax.

### Example

```typescript
import {
    SpreadsheetsApi,
    Configuration,
    FormulaValidateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SpreadsheetsApi(configuration);

let formulaValidateRequest: FormulaValidateRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.validateFormulaApiV1SpreadsheetsFormulaValidatePost_0(
    formulaValidateRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **formulaValidateRequest** | **FormulaValidateRequest**|  | |
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

