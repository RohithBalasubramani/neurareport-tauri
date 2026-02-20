# MappingPayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**catalog_allowlist** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**connection_id** | **string** |  | [optional] [default to undefined]
**dialect_hint** | **string** |  | [optional] [default to undefined]
**force_generator_rebuild** | **boolean** |  | [optional] [default to false]
**generator_dialect** | **string** |  | [optional] [default to undefined]
**keys** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**mapping** | **{ [key: string]: string; }** |  | [default to undefined]
**params_spec** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**sample_params** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**user_instructions** | **string** |  | [optional] [default to undefined]
**user_values_text** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { MappingPayload } from './api';

const instance: MappingPayload = {
    catalog_allowlist,
    connection_id,
    dialect_hint,
    force_generator_rebuild,
    generator_dialect,
    keys,
    mapping,
    params_spec,
    sample_params,
    user_instructions,
    user_values_text,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
