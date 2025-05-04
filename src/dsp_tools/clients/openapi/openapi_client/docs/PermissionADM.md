# PermissionADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**additional_information** | **str** |  | [optional] 
**permission_code** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.permission_adm import PermissionADM

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionADM from a JSON string
permission_adm_instance = PermissionADM.from_json(json)
# print the JSON string representation of the object
print(PermissionADM.to_json())

# convert the object into a dict
permission_adm_dict = permission_adm_instance.to_dict()
# create an instance of PermissionADM from a dict
permission_adm_from_dict = PermissionADM.from_dict(permission_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


