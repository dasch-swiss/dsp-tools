# CreateDefaultObjectAccessPermissionAPIRequestADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**for_project** | **str** |  | 
**for_group** | **str** |  | [optional] 
**for_resource_class** | **str** |  | [optional] 
**for_property** | **str** |  | [optional] 
**has_permissions** | [**List[PermissionADM]**](PermissionADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.create_default_object_access_permission_api_request_adm import CreateDefaultObjectAccessPermissionAPIRequestADM

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDefaultObjectAccessPermissionAPIRequestADM from a JSON string
create_default_object_access_permission_api_request_adm_instance = CreateDefaultObjectAccessPermissionAPIRequestADM.from_json(json)
# print the JSON string representation of the object
print(CreateDefaultObjectAccessPermissionAPIRequestADM.to_json())

# convert the object into a dict
create_default_object_access_permission_api_request_adm_dict = create_default_object_access_permission_api_request_adm_instance.to_dict()
# create an instance of CreateDefaultObjectAccessPermissionAPIRequestADM from a dict
create_default_object_access_permission_api_request_adm_from_dict = CreateDefaultObjectAccessPermissionAPIRequestADM.from_dict(create_default_object_access_permission_api_request_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


