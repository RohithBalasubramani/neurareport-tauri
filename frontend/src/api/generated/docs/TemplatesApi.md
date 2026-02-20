# TemplatesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**applyChatTemplateEditRouteApiV1TemplatesTemplateIdChatApplyPost**](#applychattemplateeditrouteapiv1templatestemplateidchatapplypost) | **POST** /api/v1/templates/{template_id}/chat/apply | Apply Chat Template Edit Route|
|[**chatTemplateEditRouteApiV1TemplatesTemplateIdChatPost**](#chattemplateeditrouteapiv1templatestemplateidchatpost) | **POST** /api/v1/templates/{template_id}/chat | Chat Template Edit Route|
|[**createSavedChartRouteApiV1TemplatesTemplateIdChartsSavedPost**](#createsavedchartrouteapiv1templatestemplateidchartssavedpost) | **POST** /api/v1/templates/{template_id}/charts/saved | Create Saved Chart Route|
|[**deleteSavedChartRouteApiV1TemplatesTemplateIdChartsSavedChartIdDelete**](#deletesavedchartrouteapiv1templatestemplateidchartssavedchartiddelete) | **DELETE** /api/v1/templates/{template_id}/charts/saved/{chart_id} | Delete Saved Chart Route|
|[**deleteTemplateRouteApiV1TemplatesTemplateIdDelete**](#deletetemplaterouteapiv1templatestemplateiddelete) | **DELETE** /api/v1/templates/{template_id} | Delete Template Route|
|[**duplicateTemplateApiV1TemplatesTemplateIdDuplicatePost**](#duplicatetemplateapiv1templatestemplateidduplicatepost) | **POST** /api/v1/templates/{template_id}/duplicate | Duplicate Template|
|[**editTemplateAiRouteApiV1TemplatesTemplateIdEditAiPost**](#edittemplateairouteapiv1templatestemplateideditaipost) | **POST** /api/v1/templates/{template_id}/edit-ai | Edit Template Ai Route|
|[**editTemplateManualRouteApiV1TemplatesTemplateIdEditManualPost**](#edittemplatemanualrouteapiv1templatestemplateideditmanualpost) | **POST** /api/v1/templates/{template_id}/edit-manual | Edit Template Manual Route|
|[**exportTemplateZipApiV1TemplatesTemplateIdExportGet**](#exporttemplatezipapiv1templatestemplateidexportget) | **GET** /api/v1/templates/{template_id}/export | Export Template Zip|
|[**generatorAssetsRouteApiV1TemplatesTemplateIdGeneratorAssetsV1Post**](#generatorassetsrouteapiv1templatestemplateidgeneratorassetsv1post) | **POST** /api/v1/templates/{template_id}/generator-assets/v1 | Generator Assets Route|
|[**getAllTagsApiV1TemplatesTagsAllGet**](#getalltagsapiv1templatestagsallget) | **GET** /api/v1/templates/tags/all | Get All Tags|
|[**getArtifactHeadApiV1TemplatesTemplateIdArtifactsHeadGet**](#getartifactheadapiv1templatestemplateidartifactsheadget) | **GET** /api/v1/templates/{template_id}/artifacts/head | Get Artifact Head|
|[**getArtifactManifestApiV1TemplatesTemplateIdArtifactsManifestGet**](#getartifactmanifestapiv1templatestemplateidartifactsmanifestget) | **GET** /api/v1/templates/{template_id}/artifacts/manifest | Get Artifact Manifest|
|[**getTemplateHtmlRouteApiV1TemplatesTemplateIdHtmlGet**](#gettemplatehtmlrouteapiv1templatestemplateidhtmlget) | **GET** /api/v1/templates/{template_id}/html | Get Template Html Route|
|[**importTemplateZipApiV1TemplatesImportZipPost**](#importtemplatezipapiv1templatesimportzippost) | **POST** /api/v1/templates/import-zip | Import Template Zip|
|[**listSavedChartsRouteApiV1TemplatesTemplateIdChartsSavedGet**](#listsavedchartsrouteapiv1templatestemplateidchartssavedget) | **GET** /api/v1/templates/{template_id}/charts/saved | List Saved Charts Route|
|[**listTemplatesRouteApiV1TemplatesGet**](#listtemplatesrouteapiv1templatesget) | **GET** /api/v1/templates | List Templates Route|
|[**mappingApproveApiV1TemplatesTemplateIdMappingApprovePost**](#mappingapproveapiv1templatestemplateidmappingapprovepost) | **POST** /api/v1/templates/{template_id}/mapping/approve | Mapping Approve|
|[**mappingCorrectionsPreviewApiV1TemplatesTemplateIdMappingCorrectionsPreviewPost**](#mappingcorrectionspreviewapiv1templatestemplateidmappingcorrectionspreviewpost) | **POST** /api/v1/templates/{template_id}/mapping/corrections-preview | Mapping Corrections Preview|
|[**mappingKeyOptionsApiV1TemplatesTemplateIdKeysOptionsGet**](#mappingkeyoptionsapiv1templatestemplateidkeysoptionsget) | **GET** /api/v1/templates/{template_id}/keys/options | Mapping Key Options|
|[**mappingPreviewApiV1TemplatesTemplateIdMappingPreviewPost**](#mappingpreviewapiv1templatestemplateidmappingpreviewpost) | **POST** /api/v1/templates/{template_id}/mapping/preview | Mapping Preview|
|[**recommendTemplatesRouteApiV1TemplatesRecommendPost**](#recommendtemplatesrouteapiv1templatesrecommendpost) | **POST** /api/v1/templates/recommend | Recommend Templates Route|
|[**suggestChartsRouteApiV1TemplatesTemplateIdChartsSuggestPost**](#suggestchartsrouteapiv1templatestemplateidchartssuggestpost) | **POST** /api/v1/templates/{template_id}/charts/suggest | Suggest Charts Route|
|[**templatesCatalogRouteApiV1TemplatesCatalogGet**](#templatescatalogrouteapiv1templatescatalogget) | **GET** /api/v1/templates/catalog | Templates Catalog Route|
|[**undoLastEditRouteApiV1TemplatesTemplateIdUndoLastEditPost**](#undolasteditrouteapiv1templatestemplateidundolasteditpost) | **POST** /api/v1/templates/{template_id}/undo-last-edit | Undo Last Edit Route|
|[**updateSavedChartRouteApiV1TemplatesTemplateIdChartsSavedChartIdPut**](#updatesavedchartrouteapiv1templatestemplateidchartssavedchartidput) | **PUT** /api/v1/templates/{template_id}/charts/saved/{chart_id} | Update Saved Chart Route|
|[**updateTemplateMetadataRouteApiV1TemplatesTemplateIdPatch**](#updatetemplatemetadatarouteapiv1templatestemplateidpatch) | **PATCH** /api/v1/templates/{template_id} | Update Template Metadata Route|
|[**updateTemplateTagsApiV1TemplatesTemplateIdTagsPut**](#updatetemplatetagsapiv1templatestemplateidtagsput) | **PUT** /api/v1/templates/{template_id}/tags | Update Template Tags|
|[**verifyTemplateRouteApiV1TemplatesVerifyPost**](#verifytemplaterouteapiv1templatesverifypost) | **POST** /api/v1/templates/verify | Verify Template Route|

# **applyChatTemplateEditRouteApiV1TemplatesTemplateIdChatApplyPost**
> any applyChatTemplateEditRouteApiV1TemplatesTemplateIdChatApplyPost(templateManualEditPayload)

Apply the HTML changes from a chat conversation.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    TemplateManualEditPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let templateManualEditPayload: TemplateManualEditPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.applyChatTemplateEditRouteApiV1TemplatesTemplateIdChatApplyPost(
    templateId,
    templateManualEditPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateManualEditPayload** | **TemplateManualEditPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **chatTemplateEditRouteApiV1TemplatesTemplateIdChatPost**
> any chatTemplateEditRouteApiV1TemplatesTemplateIdChatPost(templateChatPayload)

Conversational template editing endpoint.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    TemplateChatPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let templateChatPayload: TemplateChatPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.chatTemplateEditRouteApiV1TemplatesTemplateIdChatPost(
    templateId,
    templateChatPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateChatPayload** | **TemplateChatPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **createSavedChartRouteApiV1TemplatesTemplateIdChartsSavedPost**
> any createSavedChartRouteApiV1TemplatesTemplateIdChartsSavedPost(savedChartCreatePayload)

Create a saved chart for a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    SavedChartCreatePayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let savedChartCreatePayload: SavedChartCreatePayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSavedChartRouteApiV1TemplatesTemplateIdChartsSavedPost(
    templateId,
    savedChartCreatePayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **savedChartCreatePayload** | **SavedChartCreatePayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **deleteSavedChartRouteApiV1TemplatesTemplateIdChartsSavedChartIdDelete**
> any deleteSavedChartRouteApiV1TemplatesTemplateIdChartsSavedChartIdDelete()

Delete a saved chart.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let chartId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSavedChartRouteApiV1TemplatesTemplateIdChartsSavedChartIdDelete(
    templateId,
    chartId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **chartId** | [**string**] |  | defaults to undefined|
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

# **deleteTemplateRouteApiV1TemplatesTemplateIdDelete**
> any deleteTemplateRouteApiV1TemplatesTemplateIdDelete()

Delete a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTemplateRouteApiV1TemplatesTemplateIdDelete(
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **duplicateTemplateApiV1TemplatesTemplateIdDuplicatePost**
> any duplicateTemplateApiV1TemplatesTemplateIdDuplicatePost()

Duplicate a template to create a new copy.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let name: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.duplicateTemplateApiV1TemplatesTemplateIdDuplicatePost(
    templateId,
    xApiKey,
    name
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **name** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **editTemplateAiRouteApiV1TemplatesTemplateIdEditAiPost**
> any editTemplateAiRouteApiV1TemplatesTemplateIdEditAiPost(templateAiEditPayload)

Apply AI-powered edits to a template based on instructions.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    TemplateAiEditPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let templateAiEditPayload: TemplateAiEditPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.editTemplateAiRouteApiV1TemplatesTemplateIdEditAiPost(
    templateId,
    templateAiEditPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateAiEditPayload** | **TemplateAiEditPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **editTemplateManualRouteApiV1TemplatesTemplateIdEditManualPost**
> any editTemplateManualRouteApiV1TemplatesTemplateIdEditManualPost(templateManualEditPayload)

Save manual HTML edits to a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    TemplateManualEditPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let templateManualEditPayload: TemplateManualEditPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.editTemplateManualRouteApiV1TemplatesTemplateIdEditManualPost(
    templateId,
    templateManualEditPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateManualEditPayload** | **TemplateManualEditPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **exportTemplateZipApiV1TemplatesTemplateIdExportGet**
> any exportTemplateZipApiV1TemplatesTemplateIdExportGet()

Export a template as a zip file for sharing or backup.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportTemplateZipApiV1TemplatesTemplateIdExportGet(
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **generatorAssetsRouteApiV1TemplatesTemplateIdGeneratorAssetsV1Post**
> any generatorAssetsRouteApiV1TemplatesTemplateIdGeneratorAssetsV1Post(generatorAssetsPayload)

Generate assets for a PDF template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    GeneratorAssetsPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let generatorAssetsPayload: GeneratorAssetsPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generatorAssetsRouteApiV1TemplatesTemplateIdGeneratorAssetsV1Post(
    templateId,
    generatorAssetsPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **generatorAssetsPayload** | **GeneratorAssetsPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **getAllTagsApiV1TemplatesTagsAllGet**
> any getAllTagsApiV1TemplatesTagsAllGet()

Get all unique tags across all templates.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAllTagsApiV1TemplatesTagsAllGet(
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

# **getArtifactHeadApiV1TemplatesTemplateIdArtifactsHeadGet**
> any getArtifactHeadApiV1TemplatesTemplateIdArtifactsHeadGet()

Get the head (preview) of a specific artifact.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let name: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getArtifactHeadApiV1TemplatesTemplateIdArtifactsHeadGet(
    templateId,
    name,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **getArtifactManifestApiV1TemplatesTemplateIdArtifactsManifestGet**
> any getArtifactManifestApiV1TemplatesTemplateIdArtifactsManifestGet()

Get the artifact manifest for a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getArtifactManifestApiV1TemplatesTemplateIdArtifactsManifestGet(
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **getTemplateHtmlRouteApiV1TemplatesTemplateIdHtmlGet**
> any getTemplateHtmlRouteApiV1TemplatesTemplateIdHtmlGet()

Get the current HTML content of a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTemplateHtmlRouteApiV1TemplatesTemplateIdHtmlGet(
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **importTemplateZipApiV1TemplatesImportZipPost**
> TemplateImportResult importTemplateZipApiV1TemplatesImportZipPost()

Import a template from a zip file.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let file: File; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)
let name: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.importTemplateZipApiV1TemplatesImportZipPost(
    file,
    xApiKey,
    name
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **name** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TemplateImportResult**

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

# **listSavedChartsRouteApiV1TemplatesTemplateIdChartsSavedGet**
> any listSavedChartsRouteApiV1TemplatesTemplateIdChartsSavedGet()

List saved charts for a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSavedChartsRouteApiV1TemplatesTemplateIdChartsSavedGet(
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **listTemplatesRouteApiV1TemplatesGet**
> any listTemplatesRouteApiV1TemplatesGet()

List all templates with optional status filter.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let status: string; // (optional) (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTemplatesRouteApiV1TemplatesGet(
    status,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **status** | [**string**] |  | (optional) defaults to undefined|
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

# **mappingApproveApiV1TemplatesTemplateIdMappingApprovePost**
> any mappingApproveApiV1TemplatesTemplateIdMappingApprovePost(mappingPayload)

Approve mapping for a PDF template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    MappingPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let mappingPayload: MappingPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mappingApproveApiV1TemplatesTemplateIdMappingApprovePost(
    templateId,
    mappingPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **mappingPayload** | **MappingPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **mappingCorrectionsPreviewApiV1TemplatesTemplateIdMappingCorrectionsPreviewPost**
> any mappingCorrectionsPreviewApiV1TemplatesTemplateIdMappingCorrectionsPreviewPost(correctionsPreviewPayload)

Preview corrections for PDF template mapping.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    CorrectionsPreviewPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let correctionsPreviewPayload: CorrectionsPreviewPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mappingCorrectionsPreviewApiV1TemplatesTemplateIdMappingCorrectionsPreviewPost(
    templateId,
    correctionsPreviewPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **correctionsPreviewPayload** | **CorrectionsPreviewPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **mappingKeyOptionsApiV1TemplatesTemplateIdKeysOptionsGet**
> any mappingKeyOptionsApiV1TemplatesTemplateIdKeysOptionsGet()

Get available key options for template filtering.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let connectionId: string; // (optional) (default to undefined)
let tokens: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 500)
let startDate: string; // (optional) (default to undefined)
let endDate: string; // (optional) (default to undefined)
let debug: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mappingKeyOptionsApiV1TemplatesTemplateIdKeysOptionsGet(
    templateId,
    connectionId,
    tokens,
    limit,
    startDate,
    endDate,
    debug,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|
| **tokens** | [**string**] |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 500|
| **startDate** | [**string**] |  | (optional) defaults to undefined|
| **endDate** | [**string**] |  | (optional) defaults to undefined|
| **debug** | [**boolean**] |  | (optional) defaults to false|
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

# **mappingPreviewApiV1TemplatesTemplateIdMappingPreviewPost**
> any mappingPreviewApiV1TemplatesTemplateIdMappingPreviewPost()

Preview mapping for a PDF template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let connectionId: string; // (default to undefined)
let forceRefresh: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.mappingPreviewApiV1TemplatesTemplateIdMappingPreviewPost(
    templateId,
    connectionId,
    forceRefresh,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
| **connectionId** | [**string**] |  | defaults to undefined|
| **forceRefresh** | [**boolean**] |  | (optional) defaults to false|
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

# **recommendTemplatesRouteApiV1TemplatesRecommendPost**
> any recommendTemplatesRouteApiV1TemplatesRecommendPost(templateRecommendPayload)

Get AI-powered template recommendations based on user requirements.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    TemplateRecommendPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateRecommendPayload: TemplateRecommendPayload; //
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.recommendTemplatesRouteApiV1TemplatesRecommendPost(
    templateRecommendPayload,
    background,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateRecommendPayload** | **TemplateRecommendPayload**|  | |
| **background** | [**boolean**] |  | (optional) defaults to false|
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

# **suggestChartsRouteApiV1TemplatesTemplateIdChartsSuggestPost**
> any suggestChartsRouteApiV1TemplatesTemplateIdChartsSuggestPost(chartSuggestPayload)

Get chart suggestions for a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    ChartSuggestPayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let chartSuggestPayload: ChartSuggestPayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestChartsRouteApiV1TemplatesTemplateIdChartsSuggestPost(
    templateId,
    chartSuggestPayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chartSuggestPayload** | **ChartSuggestPayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **templatesCatalogRouteApiV1TemplatesCatalogGet**
> any templatesCatalogRouteApiV1TemplatesCatalogGet()

Get template catalog for browsing.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.templatesCatalogRouteApiV1TemplatesCatalogGet(
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

# **undoLastEditRouteApiV1TemplatesTemplateIdUndoLastEditPost**
> any undoLastEditRouteApiV1TemplatesTemplateIdUndoLastEditPost()

Undo the last edit made to a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.undoLastEditRouteApiV1TemplatesTemplateIdUndoLastEditPost(
    templateId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateId** | [**string**] |  | defaults to undefined|
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

# **updateSavedChartRouteApiV1TemplatesTemplateIdChartsSavedChartIdPut**
> any updateSavedChartRouteApiV1TemplatesTemplateIdChartsSavedChartIdPut(savedChartUpdatePayload)

Update a saved chart.

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    SavedChartUpdatePayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let chartId: string; // (default to undefined)
let savedChartUpdatePayload: SavedChartUpdatePayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSavedChartRouteApiV1TemplatesTemplateIdChartsSavedChartIdPut(
    templateId,
    chartId,
    savedChartUpdatePayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **savedChartUpdatePayload** | **SavedChartUpdatePayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
| **chartId** | [**string**] |  | defaults to undefined|
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

# **updateTemplateMetadataRouteApiV1TemplatesTemplateIdPatch**
> any updateTemplateMetadataRouteApiV1TemplatesTemplateIdPatch(templateUpdatePayload)

Update template metadata (name, description, etc.).

### Example

```typescript
import {
    TemplatesApi,
    Configuration,
    TemplateUpdatePayload
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let templateUpdatePayload: TemplateUpdatePayload; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTemplateMetadataRouteApiV1TemplatesTemplateIdPatch(
    templateId,
    templateUpdatePayload,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **templateUpdatePayload** | **TemplateUpdatePayload**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **updateTemplateTagsApiV1TemplatesTemplateIdTagsPut**
> any updateTemplateTagsApiV1TemplatesTemplateIdTagsPut(requestBody)

Update tags for a template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let templateId: string; // (default to undefined)
let requestBody: { [key: string]: any; }; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTemplateTagsApiV1TemplatesTemplateIdTagsPut(
    templateId,
    requestBody,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
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

# **verifyTemplateRouteApiV1TemplatesVerifyPost**
> any verifyTemplateRouteApiV1TemplatesVerifyPost()

Verify and process a PDF template.

### Example

```typescript
import {
    TemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TemplatesApi(configuration);

let file: File; // (default to undefined)
let background: boolean; // (optional) (default to false)
let xApiKey: string; // (optional) (default to undefined)
let connectionId: string; // (optional) (default to undefined)
let refineIters: number; // (optional) (default to 0)

const { status, data } = await apiInstance.verifyTemplateRouteApiV1TemplatesVerifyPost(
    file,
    background,
    xApiKey,
    connectionId,
    refineIters
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**File**] |  | defaults to undefined|
| **background** | [**boolean**] |  | (optional) defaults to false|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|
| **connectionId** | [**string**] |  | (optional) defaults to undefined|
| **refineIters** | [**number**] |  | (optional) defaults to 0|


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

