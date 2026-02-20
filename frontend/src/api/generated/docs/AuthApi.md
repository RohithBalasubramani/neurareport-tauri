# AuthApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**authJwtLoginApiV1AuthJwtLoginPost**](#authjwtloginapiv1authjwtloginpost) | **POST** /api/v1/auth/jwt/login | Auth:Jwt.Login|
|[**authJwtLogoutApiV1AuthJwtLogoutPost**](#authjwtlogoutapiv1authjwtlogoutpost) | **POST** /api/v1/auth/jwt/logout | Auth:Jwt.Logout|
|[**registerRegisterApiV1AuthRegisterPost**](#registerregisterapiv1authregisterpost) | **POST** /api/v1/auth/register | Register:Register|

# **authJwtLoginApiV1AuthJwtLoginPost**
> BearerResponse authJwtLoginApiV1AuthJwtLoginPost()


### Example

```typescript
import {
    AuthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let password: string; // (default to undefined)
let username: string; // (default to undefined)
let clientId: string; // (optional) (default to undefined)
let clientSecret: string; // (optional) (default to undefined)
let grantType: string; // (optional) (default to undefined)
let scope: string; // (optional) (default to '')

const { status, data } = await apiInstance.authJwtLoginApiV1AuthJwtLoginPost(
    password,
    username,
    clientId,
    clientSecret,
    grantType,
    scope
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **password** | [**string**] |  | defaults to undefined|
| **username** | [**string**] |  | defaults to undefined|
| **clientId** | [**string**] |  | (optional) defaults to undefined|
| **clientSecret** | [**string**] |  | (optional) defaults to undefined|
| **grantType** | [**string**] |  | (optional) defaults to undefined|
| **scope** | [**string**] |  | (optional) defaults to ''|


### Return type

**BearerResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad Request |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **authJwtLogoutApiV1AuthJwtLogoutPost**
> any authJwtLogoutApiV1AuthJwtLogoutPost()


### Example

```typescript
import {
    AuthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

const { status, data } = await apiInstance.authJwtLogoutApiV1AuthJwtLogoutPost();
```

### Parameters
This endpoint does not have any parameters.


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
|**401** | Missing token or inactive user. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **registerRegisterApiV1AuthRegisterPost**
> UserRead registerRegisterApiV1AuthRegisterPost(userCreate)


### Example

```typescript
import {
    AuthApi,
    Configuration,
    UserCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let userCreate: UserCreate; //

const { status, data } = await apiInstance.registerRegisterApiV1AuthRegisterPost(
    userCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userCreate** | **UserCreate**|  | |


### Return type

**UserRead**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**400** | Bad Request |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

