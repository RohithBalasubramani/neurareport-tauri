# ComplianceCheckResponse

Compliance check result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**checked_regulations** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**compliant** | **boolean** |  | [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**recommendations** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**violations** | [**Array&lt;ComplianceViolation&gt;**](ComplianceViolation.md) |  | [optional] [default to undefined]
**warnings** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { ComplianceCheckResponse } from './api';

const instance: ComplianceCheckResponse = {
    checked_regulations,
    compliant,
    processing_time_ms,
    recommendations,
    violations,
    warnings,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
