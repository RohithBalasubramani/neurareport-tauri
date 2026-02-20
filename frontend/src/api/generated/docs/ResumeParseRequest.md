# ResumeParseRequest

Request to parse a resume.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **string** |  | [optional] [default to undefined]
**extract_skills** | **boolean** |  | [optional] [default to true]
**file_path** | **string** |  | [optional] [default to undefined]
**language** | **string** |  | [optional] [default to 'en']
**match_job_description** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ResumeParseRequest } from './api';

const instance: ResumeParseRequest = {
    content,
    extract_skills,
    file_path,
    language,
    match_job_description,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
