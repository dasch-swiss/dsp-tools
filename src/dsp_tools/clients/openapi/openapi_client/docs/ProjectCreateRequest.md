# ProjectCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**ProjectIri**](ProjectIri.md) |  | [optional] 
**shortname** | [**Shortname**](Shortname.md) |  | 
**shortcode** | [**Shortcode**](Shortcode.md) |  | 
**longname** | [**Longname**](Longname.md) |  | [optional] 
**description** | [**List[Description]**](Description.md) |  | [optional] 
**keywords** | [**List[Keyword]**](Keyword.md) |  | [optional] 
**logo** | [**Logo**](Logo.md) |  | [optional] 
**status** | [**Status**](Status.md) |  | 
**selfjoin** | [**SelfJoin**](SelfJoin.md) |  | 

## Example

```python
from openapi_client.models.project_create_request import ProjectCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectCreateRequest from a JSON string
project_create_request_instance = ProjectCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ProjectCreateRequest.to_json())

# convert the object into a dict
project_create_request_dict = project_create_request_instance.to_dict()
# create an instance of ProjectCreateRequest from a dict
project_create_request_from_dict = ProjectCreateRequest.from_dict(project_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


