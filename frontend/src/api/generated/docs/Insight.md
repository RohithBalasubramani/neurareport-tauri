# Insight

A generated insight.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **number** |  | [default to undefined]
**data** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**description** | **string** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**related_columns** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**severity** | [**InsightSeverity**](InsightSeverity.md) |  | [optional] [default to undefined]
**title** | **string** |  | [default to undefined]
**type** | [**InsightType**](InsightType.md) |  | [default to undefined]
**visualization_hint** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { Insight } from './api';

const instance: Insight = {
    confidence,
    data,
    description,
    id,
    related_columns,
    severity,
    title,
    type,
    visualization_hint,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
