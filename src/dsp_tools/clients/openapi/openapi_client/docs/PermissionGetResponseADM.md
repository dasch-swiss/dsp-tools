# PermissionGetResponseADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**administrative_permission** | [**AdministrativePermissionADM**](AdministrativePermissionADM.md) |  | 
**default_object_access_permission** | [**DefaultObjectAccessPermissionADM**](DefaultObjectAccessPermissionADM.md) |  | 

## Example

```python
from openapi_client.models.permission_get_response_adm import PermissionGetResponseADM

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionGetResponseADM from a JSON string
permission_get_response_adm_instance = PermissionGetResponseADM.from_json(json)
# print the JSON string representation of the object
print(PermissionGetResponseADM.to_json())

# convert the object into a dict
permission_get_response_adm_dict = permission_get_response_adm_instance.to_dict()
# create an instance of PermissionGetResponseADM from a dict
permission_get_response_adm_from_dict = PermissionGetResponseADM.from_dict(permission_get_response_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


