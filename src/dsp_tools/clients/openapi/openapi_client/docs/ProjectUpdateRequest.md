# ProjectUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**shortname** | [**Shortname**](Shortname.md) |  | [optional] 
**longname** | [**Longname**](Longname.md) |  | [optional] 
**description** | [**List[Description]**](Description.md) |  | [optional] 
**keywords** | [**List[Keyword]**](Keyword.md) |  | [optional] 
**logo** | [**Logo**](Logo.md) |  | [optional] 
**status** | [**Status**](Status.md) |  | [optional] 
**selfjoin** | [**SelfJoin**](SelfJoin.md) |  | [optional] 

## Example

```python
from openapi_client.models.project_update_request import ProjectUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectUpdateRequest from a JSON string
project_update_request_instance = ProjectUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(ProjectUpdateRequest.to_json())

# convert the object into a dict
project_update_request_dict = project_update_request_instance.to_dict()
# create an instance of ProjectUpdateRequest from a dict
project_update_request_from_dict = ProjectUpdateRequest.from_dict(project_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


