# Project


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**ProjectIri**](ProjectIri.md) |  | 
**shortname** | [**Shortname**](Shortname.md) |  | 
**shortcode** | [**Shortcode**](Shortcode.md) |  | 
**longname** | [**Longname**](Longname.md) |  | [optional] 
**description** | [**List[StringLiteralV2]**](StringLiteralV2.md) |  | [optional] 
**keywords** | **List[str]** |  | [optional] 
**logo** | [**Logo**](Logo.md) |  | [optional] 
**ontologies** | **List[str]** |  | [optional] 
**status** | [**Status**](Status.md) |  | 
**selfjoin** | [**SelfJoin**](SelfJoin.md) |  | 

## Example

```python
from openapi_client.models.project import Project

# TODO update the JSON string below
json = "{}"
# create an instance of Project from a JSON string
project_instance = Project.from_json(json)
# print the JSON string representation of the object
print(Project.to_json())

# convert the object into a dict
project_dict = project_instance.to_dict()
# create an instance of Project from a dict
project_from_dict = Project.from_dict(project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


