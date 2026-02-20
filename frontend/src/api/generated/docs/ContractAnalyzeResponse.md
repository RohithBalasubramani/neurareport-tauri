# ContractAnalyzeResponse

Analyzed contract data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**clauses** | [**Array&lt;ContractClause&gt;**](ContractClause.md) |  | [optional] [default to undefined]
**confidence_score** | **number** |  | [default to undefined]
**contract_type** | **string** |  | [optional] [default to undefined]
**currency** | **string** |  | [optional] [default to undefined]
**effective_date** | **string** |  | [optional] [default to undefined]
**expiration_date** | **string** |  | [optional] [default to undefined]
**key_dates** | **{ [key: string]: string; }** |  | [optional] [default to undefined]
**obligations** | [**Array&lt;ContractObligation&gt;**](ContractObligation.md) |  | [optional] [default to undefined]
**overall_risk_level** | [**RiskLevel**](RiskLevel.md) |  | [optional] [default to undefined]
**parties** | [**Array&lt;ContractParty&gt;**](ContractParty.md) |  | [optional] [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**recommendations** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**risk_summary** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**summary** | **string** |  | [optional] [default to undefined]
**title** | **string** |  | [optional] [default to undefined]
**total_value** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { ContractAnalyzeResponse } from './api';

const instance: ContractAnalyzeResponse = {
    clauses,
    confidence_score,
    contract_type,
    currency,
    effective_date,
    expiration_date,
    key_dates,
    obligations,
    overall_risk_level,
    parties,
    processing_time_ms,
    recommendations,
    risk_summary,
    summary,
    title,
    total_value,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
