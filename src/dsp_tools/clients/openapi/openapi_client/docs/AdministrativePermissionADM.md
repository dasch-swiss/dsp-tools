# AdministrativePermissionADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**iri** | **str** |  | 
**for_project** | **str** |  | 
**for_group** | **str** |  | 
**has_permissions** | [**List[PermissionADM]**](PermissionADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.administrative_permission_adm import AdministrativePermissionADM

# TODO update the JSON string below
json = "{}"
# create an instance of AdministrativePermissionADM from a JSON string
administrative_permission_adm_instance = AdministrativePermissionADM.from_json(json)
# print the JSON string representation of the object
print(AdministrativePermissionADM.to_json())

# convert the object into a dict
administrative_permission_adm_dict = administrative_permission_adm_instance.to_dict()
# create an instance of AdministrativePermissionADM from a dict
administrative_permission_adm_from_dict = AdministrativePermissionADM.from_dict(administrative_permission_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


