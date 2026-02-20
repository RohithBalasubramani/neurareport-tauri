# ContractAnalyzeRequest

Request to analyze a contract.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**analyze_risks** | **boolean** |  | [optional] [default to true]
**compare_to_standard** | **boolean** |  | [optional] [default to false]
**content** | **string** |  | [optional] [default to undefined]
**extract_obligations** | **boolean** |  | [optional] [default to true]
**file_path** | **string** |  | [optional] [default to undefined]
**language** | **string** |  | [optional] [default to 'en']

## Example

```typescript
import { ContractAnalyzeRequest } from './api';

const instance: ContractAnalyzeRequest = {
    analyze_risks,
    compare_to_standard,
    content,
    extract_obligations,
    file_path,
    language,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
