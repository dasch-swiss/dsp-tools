# ProjectExportInfoResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_shortcode** | **str** |  | 
**location** | **str** |  | 

## Example

```python
from openapi_client.models.project_export_info_response import ProjectExportInfoResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectExportInfoResponse from a JSON string
project_export_info_response_instance = ProjectExportInfoResponse.from_json(json)
# print the JSON string representation of the object
print(ProjectExportInfoResponse.to_json())

# convert the object into a dict
project_export_info_response_dict = project_export_info_response_instance.to_dict()
# create an instance of ProjectExportInfoResponse from a dict
project_export_info_response_from_dict = ProjectExportInfoResponse.from_dict(project_export_info_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


