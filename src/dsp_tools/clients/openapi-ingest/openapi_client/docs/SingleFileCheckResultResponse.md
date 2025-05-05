# SingleFileCheckResultResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filename** | **str** |  | 
**checksum_matches** | **bool** |  | 

## Example

```python
from openapi_client.models.single_file_check_result_response import SingleFileCheckResultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SingleFileCheckResultResponse from a JSON string
single_file_check_result_response_instance = SingleFileCheckResultResponse.from_json(json)
# print the JSON string representation of the object
print(SingleFileCheckResultResponse.to_json())

# convert the object into a dict
single_file_check_result_response_dict = single_file_check_result_response_instance.to_dict()
# create an instance of SingleFileCheckResultResponse from a dict
single_file_check_result_response_from_dict = SingleFileCheckResultResponse.from_dict(single_file_check_result_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


