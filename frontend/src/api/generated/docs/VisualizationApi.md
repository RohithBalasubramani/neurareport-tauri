# VisualizationApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**exportAsMermaidApiV1VisualizationDiagramsDiagramIdMermaidGet**](#exportasmermaidapiv1visualizationdiagramsdiagramidmermaidget) | **GET** /api/v1/visualization/diagrams/{diagram_id}/mermaid | Export As Mermaid|
|[**exportAsPngApiV1VisualizationDiagramsDiagramIdPngGet**](#exportaspngapiv1visualizationdiagramsdiagramidpngget) | **GET** /api/v1/visualization/diagrams/{diagram_id}/png | Export As Png|
|[**exportAsSvgApiV1VisualizationDiagramsDiagramIdSvgGet**](#exportassvgapiv1visualizationdiagramsdiagramidsvgget) | **GET** /api/v1/visualization/diagrams/{diagram_id}/svg | Export As Svg|
|[**generateFlowchartApiV1VisualizationDiagramsFlowchartPost**](#generateflowchartapiv1visualizationdiagramsflowchartpost) | **POST** /api/v1/visualization/diagrams/flowchart | Generate Flowchart|
|[**generateGanttApiV1VisualizationDiagramsGanttPost**](#generateganttapiv1visualizationdiagramsganttpost) | **POST** /api/v1/visualization/diagrams/gantt | Generate Gantt|
|[**generateKanbanApiV1VisualizationDiagramsKanbanPost**](#generatekanbanapiv1visualizationdiagramskanbanpost) | **POST** /api/v1/visualization/diagrams/kanban | Generate Kanban|
|[**generateMindmapApiV1VisualizationDiagramsMindmapPost**](#generatemindmapapiv1visualizationdiagramsmindmappost) | **POST** /api/v1/visualization/diagrams/mindmap | Generate Mindmap|
|[**generateNetworkGraphApiV1VisualizationDiagramsNetworkPost**](#generatenetworkgraphapiv1visualizationdiagramsnetworkpost) | **POST** /api/v1/visualization/diagrams/network | Generate Network Graph|
|[**generateOrgChartApiV1VisualizationDiagramsOrgChartPost**](#generateorgchartapiv1visualizationdiagramsorgchartpost) | **POST** /api/v1/visualization/diagrams/org-chart | Generate Org Chart|
|[**generateSequenceDiagramApiV1VisualizationDiagramsSequencePost**](#generatesequencediagramapiv1visualizationdiagramssequencepost) | **POST** /api/v1/visualization/diagrams/sequence | Generate Sequence Diagram|
|[**generateSparklinesApiV1VisualizationChartsSparklinesPost**](#generatesparklinesapiv1visualizationchartssparklinespost) | **POST** /api/v1/visualization/charts/sparklines | Generate Sparklines|
|[**generateTimelineApiV1VisualizationDiagramsTimelinePost**](#generatetimelineapiv1visualizationdiagramstimelinepost) | **POST** /api/v1/visualization/diagrams/timeline | Generate Timeline|
|[**generateWordcloudApiV1VisualizationDiagramsWordcloudPost**](#generatewordcloudapiv1visualizationdiagramswordcloudpost) | **POST** /api/v1/visualization/diagrams/wordcloud | Generate Wordcloud|
|[**listChartTypesApiV1VisualizationTypesChartsGet**](#listcharttypesapiv1visualizationtypeschartsget) | **GET** /api/v1/visualization/types/charts | List Chart Types|
|[**listDiagramTypesApiV1VisualizationTypesDiagramsGet**](#listdiagramtypesapiv1visualizationtypesdiagramsget) | **GET** /api/v1/visualization/types/diagrams | List Diagram Types|
|[**tableToChartApiV1VisualizationChartsFromTablePost**](#tabletochartapiv1visualizationchartsfromtablepost) | **POST** /api/v1/visualization/charts/from-table | Table To Chart|

# **exportAsMermaidApiV1VisualizationDiagramsDiagramIdMermaidGet**
> any exportAsMermaidApiV1VisualizationDiagramsDiagramIdMermaidGet()

Export diagram as Mermaid.js syntax.  Returns:     Mermaid.js code

### Example

```typescript
import {
    VisualizationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let diagramId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportAsMermaidApiV1VisualizationDiagramsDiagramIdMermaidGet(
    diagramId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **diagramId** | [**string**] |  | defaults to undefined|
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

# **exportAsPngApiV1VisualizationDiagramsDiagramIdPngGet**
> any exportAsPngApiV1VisualizationDiagramsDiagramIdPngGet()

Export diagram as PNG.  Returns:     PNG image as streaming response

### Example

```typescript
import {
    VisualizationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let diagramId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportAsPngApiV1VisualizationDiagramsDiagramIdPngGet(
    diagramId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **diagramId** | [**string**] |  | defaults to undefined|
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

# **exportAsSvgApiV1VisualizationDiagramsDiagramIdSvgGet**
> any exportAsSvgApiV1VisualizationDiagramsDiagramIdSvgGet()

Export diagram as SVG.  Returns:     SVG content

### Example

```typescript
import {
    VisualizationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let diagramId: string; // (default to undefined)
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportAsSvgApiV1VisualizationDiagramsDiagramIdSvgGet(
    diagramId,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **diagramId** | [**string**] |  | defaults to undefined|
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

# **generateFlowchartApiV1VisualizationDiagramsFlowchartPost**
> any generateFlowchartApiV1VisualizationDiagramsFlowchartPost(flowchartRequest)

Generate a flowchart from a process description.  Returns:     DiagramSpec for the flowchart

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    FlowchartRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let flowchartRequest: FlowchartRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateFlowchartApiV1VisualizationDiagramsFlowchartPost(
    flowchartRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **flowchartRequest** | **FlowchartRequest**|  | |
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

# **generateGanttApiV1VisualizationDiagramsGanttPost**
> any generateGanttApiV1VisualizationDiagramsGanttPost(ganttRequest)

Generate a Gantt chart.  Returns:     DiagramSpec for the Gantt chart

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    GanttRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let ganttRequest: GanttRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateGanttApiV1VisualizationDiagramsGanttPost(
    ganttRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **ganttRequest** | **GanttRequest**|  | |
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

# **generateKanbanApiV1VisualizationDiagramsKanbanPost**
> any generateKanbanApiV1VisualizationDiagramsKanbanPost(kanbanRequest)

Generate a Kanban board visualization.  Returns:     DiagramSpec for the Kanban board

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    KanbanRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let kanbanRequest: KanbanRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateKanbanApiV1VisualizationDiagramsKanbanPost(
    kanbanRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **kanbanRequest** | **KanbanRequest**|  | |
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

# **generateMindmapApiV1VisualizationDiagramsMindmapPost**
> any generateMindmapApiV1VisualizationDiagramsMindmapPost(mindmapRequest)

Generate a mind map from document content.  Returns:     DiagramSpec for the mind map

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    MindmapRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let mindmapRequest: MindmapRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateMindmapApiV1VisualizationDiagramsMindmapPost(
    mindmapRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **mindmapRequest** | **MindmapRequest**|  | |
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

# **generateNetworkGraphApiV1VisualizationDiagramsNetworkPost**
> any generateNetworkGraphApiV1VisualizationDiagramsNetworkPost(networkGraphRequest)

Generate a network/relationship graph.  Returns:     DiagramSpec for the network graph

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    NetworkGraphRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let networkGraphRequest: NetworkGraphRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateNetworkGraphApiV1VisualizationDiagramsNetworkPost(
    networkGraphRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **networkGraphRequest** | **NetworkGraphRequest**|  | |
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

# **generateOrgChartApiV1VisualizationDiagramsOrgChartPost**
> any generateOrgChartApiV1VisualizationDiagramsOrgChartPost(orgChartRequest)

Generate an organization chart.  Returns:     DiagramSpec for the org chart

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    OrgChartRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let orgChartRequest: OrgChartRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateOrgChartApiV1VisualizationDiagramsOrgChartPost(
    orgChartRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **orgChartRequest** | **OrgChartRequest**|  | |
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

# **generateSequenceDiagramApiV1VisualizationDiagramsSequencePost**
> any generateSequenceDiagramApiV1VisualizationDiagramsSequencePost(sequenceDiagramRequest)

Generate a sequence diagram.  Returns:     DiagramSpec for the sequence diagram

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    SequenceDiagramRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let sequenceDiagramRequest: SequenceDiagramRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateSequenceDiagramApiV1VisualizationDiagramsSequencePost(
    sequenceDiagramRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sequenceDiagramRequest** | **SequenceDiagramRequest**|  | |
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

# **generateSparklinesApiV1VisualizationChartsSparklinesPost**
> any generateSparklinesApiV1VisualizationChartsSparklinesPost(sparklineRequest)

Generate inline sparkline charts.  Returns:     List of ChartSpecs for sparklines

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    SparklineRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let sparklineRequest: SparklineRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateSparklinesApiV1VisualizationChartsSparklinesPost(
    sparklineRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sparklineRequest** | **SparklineRequest**|  | |
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

# **generateTimelineApiV1VisualizationDiagramsTimelinePost**
> any generateTimelineApiV1VisualizationDiagramsTimelinePost(timelineRequest)

Generate a timeline visualization.  Returns:     DiagramSpec for the timeline

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    TimelineRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let timelineRequest: TimelineRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateTimelineApiV1VisualizationDiagramsTimelinePost(
    timelineRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **timelineRequest** | **TimelineRequest**|  | |
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

# **generateWordcloudApiV1VisualizationDiagramsWordcloudPost**
> any generateWordcloudApiV1VisualizationDiagramsWordcloudPost(wordcloudRequest)

Generate a word cloud from text.  Returns:     DiagramSpec for the word cloud

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    WordcloudRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let wordcloudRequest: WordcloudRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.generateWordcloudApiV1VisualizationDiagramsWordcloudPost(
    wordcloudRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **wordcloudRequest** | **WordcloudRequest**|  | |
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

# **listChartTypesApiV1VisualizationTypesChartsGet**
> any listChartTypesApiV1VisualizationTypesChartsGet()

List available chart types.

### Example

```typescript
import {
    VisualizationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listChartTypesApiV1VisualizationTypesChartsGet(
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

# **listDiagramTypesApiV1VisualizationTypesDiagramsGet**
> any listDiagramTypesApiV1VisualizationTypesDiagramsGet()

List available diagram types.

### Example

```typescript
import {
    VisualizationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDiagramTypesApiV1VisualizationTypesDiagramsGet(
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

# **tableToChartApiV1VisualizationChartsFromTablePost**
> any tableToChartApiV1VisualizationChartsFromTablePost(tableToChartRequest)

Convert table data to a chart.  Returns:     ChartSpec for the chart

### Example

```typescript
import {
    VisualizationApi,
    Configuration,
    TableToChartRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VisualizationApi(configuration);

let tableToChartRequest: TableToChartRequest; //
let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.tableToChartApiV1VisualizationChartsFromTablePost(
    tableToChartRequest,
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **tableToChartRequest** | **TableToChartRequest**|  | |
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

