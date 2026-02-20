# CreateWatcherRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_import** | **boolean** | Auto-import files | [optional] [default to true]
**delete_after_import** | **boolean** | Delete after import | [optional] [default to false]
**ignore_patterns** | **Array&lt;string&gt;** | Patterns to ignore | [optional] [default to undefined]
**path** | **string** | Folder path to watch | [default to undefined]
**patterns** | **Array&lt;string&gt;** | File patterns to match | [optional] [default to undefined]
**recursive** | **boolean** | Watch subdirectories | [optional] [default to true]
**tags** | **Array&lt;string&gt;** | Tags to apply | [optional] [default to undefined]
**target_collection** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CreateWatcherRequest } from './api';

const instance: CreateWatcherRequest = {
    auto_import,
    delete_after_import,
    ignore_patterns,
    path,
    patterns,
    recursive,
    tags,
    target_collection,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
