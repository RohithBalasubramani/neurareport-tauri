# ResumeParseResponse

Parsed resume data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**certifications** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**confidence_score** | **number** |  | [default to undefined]
**education** | [**Array&lt;Education&gt;**](Education.md) |  | [optional] [default to undefined]
**email** | **string** |  | [optional] [default to undefined]
**experience** | [**Array&lt;WorkExperience&gt;**](WorkExperience.md) |  | [optional] [default to undefined]
**github_url** | **string** |  | [optional] [default to undefined]
**job_match_details** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**job_match_score** | **number** |  | [optional] [default to undefined]
**languages** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**linkedin_url** | **string** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**phone** | **string** |  | [optional] [default to undefined]
**portfolio_url** | **string** |  | [optional] [default to undefined]
**processing_time_ms** | **number** |  | [default to undefined]
**raw_text** | **string** |  | [optional] [default to undefined]
**skills** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**summary** | **string** |  | [optional] [default to undefined]
**total_years_experience** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { ResumeParseResponse } from './api';

const instance: ResumeParseResponse = {
    certifications,
    confidence_score,
    education,
    email,
    experience,
    github_url,
    job_match_details,
    job_match_score,
    languages,
    linkedin_url,
    location,
    name,
    phone,
    portfolio_url,
    processing_time_ms,
    raw_text,
    skills,
    summary,
    total_years_experience,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
