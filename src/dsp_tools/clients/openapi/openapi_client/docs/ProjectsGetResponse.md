# ProjectsGetResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**projects** | [**List[Project]**](Project.md) |  | [optional] 

## Example

```python
from openapi_client.models.projects_get_response import ProjectsGetResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectsGetResponse from a JSON string
projects_get_response_instance = ProjectsGetResponse.from_json(json)
# print the JSON string representation of the object
print(ProjectsGetResponse.to_json())

# convert the object into a dict
projects_get_response_dict = projects_get_response_instance.to_dict()
# create an instance of ProjectsGetResponse from a dict
projects_get_response_from_dict = ProjectsGetResponse.from_dict(projects_get_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


