# ContractClause

Extracted contract clause.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**clause_type** | [**ContractClauseType**](ContractClauseType.md) |  | [default to undefined]
**confidence** | [**ConfidenceLevel**](ConfidenceLevel.md) |  | [optional] [default to undefined]
**end_position** | **number** |  | [optional] [default to undefined]
**page_number** | **number** |  | [optional] [default to undefined]
**risk_explanation** | **string** |  | [optional] [default to undefined]
**risk_level** | [**RiskLevel**](RiskLevel.md) |  | [optional] [default to undefined]
**start_position** | **number** |  | [optional] [default to undefined]
**suggestions** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**text** | **string** |  | [default to undefined]
**title** | **string** |  | [default to undefined]

## Example

```typescript
import { ContractClause } from './api';

const instance: ContractClause = {
    clause_type,
    confidence,
    end_position,
    page_number,
    risk_explanation,
    risk_level,
    start_position,
    suggestions,
    text,
    title,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
