# ComplianceViolation

A compliance violation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **string** |  | [default to undefined]
**location** | **string** |  | [default to undefined]
**remediation** | **string** |  | [default to undefined]
**rule** | [**ComplianceRule**](ComplianceRule.md) |  | [default to undefined]
**severity** | [**RiskLevel**](RiskLevel.md) |  | [default to undefined]

## Example

```typescript
import { ComplianceViolation } from './api';

const instance: ComplianceViolation = {
    description,
    location,
    remediation,
    rule,
    severity,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
