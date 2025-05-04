# PermissionsDataADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**groups_per_project** | **Dict[str, List[str]]** |  | 
**administrative_permissions_per_project** | **Dict[str, List[PermissionADM]]** |  | 

## Example

```python
from openapi_client.models.permissions_data_adm import PermissionsDataADM

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionsDataADM from a JSON string
permissions_data_adm_instance = PermissionsDataADM.from_json(json)
# print the JSON string representation of the object
print(PermissionsDataADM.to_json())

# convert the object into a dict
permissions_data_adm_dict = permissions_data_adm_instance.to_dict()
# create an instance of PermissionsDataADM from a dict
permissions_data_adm_from_dict = PermissionsDataADM.from_dict(permissions_data_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


