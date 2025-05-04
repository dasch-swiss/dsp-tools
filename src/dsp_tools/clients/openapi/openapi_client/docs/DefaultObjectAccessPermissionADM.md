# DefaultObjectAccessPermissionADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**iri** | **str** |  | 
**for_project** | **str** |  | 
**for_group** | **str** |  | [optional] 
**for_resource_class** | **str** |  | [optional] 
**for_property** | **str** |  | [optional] 
**has_permissions** | [**List[PermissionADM]**](PermissionADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.default_object_access_permission_adm import DefaultObjectAccessPermissionADM

# TODO update the JSON string below
json = "{}"
# create an instance of DefaultObjectAccessPermissionADM from a JSON string
default_object_access_permission_adm_instance = DefaultObjectAccessPermissionADM.from_json(json)
# print the JSON string representation of the object
print(DefaultObjectAccessPermissionADM.to_json())

# convert the object into a dict
default_object_access_permission_adm_dict = default_object_access_permission_adm_instance.to_dict()
# create an instance of DefaultObjectAccessPermissionADM from a dict
default_object_access_permission_adm_from_dict = DefaultObjectAccessPermissionADM.from_dict(default_object_access_permission_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


