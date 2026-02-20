# EnrichmentSourceCreate

Request to create an enrichment source.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cache_ttl_hours** | **number** |  | [optional] [default to 24]
**config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**type** | [**EnrichmentSourceType**](EnrichmentSourceType.md) |  | [default to undefined]

## Example

```typescript
import { EnrichmentSourceCreate } from './api';

const instance: EnrichmentSourceCreate = {
    cache_ttl_hours,
    config,
    description,
    name,
    type,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
