# HealthApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**emailConnectionTestApiV1HealthEmailTestGet**](#emailconnectiontestapiv1healthemailtestget) | **GET** /api/v1/health/email/test | Email Connection Test|
|[**emailHealthApiV1HealthEmailGet**](#emailhealthapiv1healthemailget) | **GET** /api/v1/health/email | Email Health|
|[**healthApiV1HealthGet**](#healthapiv1healthget) | **GET** /api/v1/health | Health|
|[**healthDetailedApiV1HealthDetailedGet**](#healthdetailedapiv1healthdetailedget) | **GET** /api/v1/health/detailed | Health Detailed|
|[**healthzApiV1HealthzGet**](#healthzapiv1healthzget) | **GET** /api/v1/healthz | Healthz|
|[**readyApiV1ReadyGet**](#readyapiv1readyget) | **GET** /api/v1/ready | Ready|
|[**readyzApiV1ReadyzGet**](#readyzapiv1readyzget) | **GET** /api/v1/readyz | Readyz|
|[**refreshEmailConfigApiV1HealthEmailRefreshPost**](#refreshemailconfigapiv1healthemailrefreshpost) | **POST** /api/v1/health/email/refresh | Refresh Email Config|
|[**schedulerHealthApiV1HealthSchedulerGet**](#schedulerhealthapiv1healthschedulerget) | **GET** /api/v1/health/scheduler | Scheduler Health|
|[**tokenUsageApiV1HealthTokenUsageGet**](#tokenusageapiv1healthtokenusageget) | **GET** /api/v1/health/token-usage | Token Usage|

# **emailConnectionTestApiV1HealthEmailTestGet**
> { [key: string]: any; } emailConnectionTestApiV1HealthEmailTestGet()

Test SMTP connection (without sending an email).

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.emailConnectionTestApiV1HealthEmailTestGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **emailHealthApiV1HealthEmailGet**
> { [key: string]: any; } emailHealthApiV1HealthEmailGet()

Check email/SMTP configuration and optionally test connection.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.emailHealthApiV1HealthEmailGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **healthApiV1HealthGet**
> { [key: string]: any; } healthApiV1HealthGet()

Basic health check - fast, for load balancer probes.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthApiV1HealthGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **healthDetailedApiV1HealthDetailedGet**
> { [key: string]: any; } healthDetailedApiV1HealthDetailedGet()

Comprehensive health check with all dependencies.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

let xApiKey: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.healthDetailedApiV1HealthDetailedGet(
    xApiKey
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xApiKey** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **healthzApiV1HealthzGet**
> { [key: string]: string | null; } healthzApiV1HealthzGet()

Kubernetes-style liveness probe.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthzApiV1HealthzGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: string | null; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **readyApiV1ReadyGet**
> { [key: string]: any; } readyApiV1ReadyGet()

Kubernetes-style readiness probe - checks if app can serve requests.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.readyApiV1ReadyGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **readyzApiV1ReadyzGet**
> { [key: string]: any; } readyzApiV1ReadyzGet()

Compatibility alias for readiness probe.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.readyzApiV1ReadyzGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **refreshEmailConfigApiV1HealthEmailRefreshPost**
> { [key: string]: any; } refreshEmailConfigApiV1HealthEmailRefreshPost()

Refresh email configuration from environment variables.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.refreshEmailConfigApiV1HealthEmailRefreshPost();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **schedulerHealthApiV1HealthSchedulerGet**
> { [key: string]: any; } schedulerHealthApiV1HealthSchedulerGet()

Check scheduler status with detailed information.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.schedulerHealthApiV1HealthSchedulerGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **tokenUsageApiV1HealthTokenUsageGet**
> { [key: string]: any; } tokenUsageApiV1HealthTokenUsageGet()

Get LLM token usage statistics.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.tokenUsageApiV1HealthTokenUsageGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

