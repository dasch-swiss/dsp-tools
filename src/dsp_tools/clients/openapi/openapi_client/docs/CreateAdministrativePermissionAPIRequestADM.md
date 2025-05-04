# CreateAdministrativePermissionAPIRequestADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**for_project** | **str** |  | 
**for_group** | **str** |  | 
**has_permissions** | [**List[PermissionADM]**](PermissionADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.create_administrative_permission_api_request_adm import CreateAdministrativePermissionAPIRequestADM

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAdministrativePermissionAPIRequestADM from a JSON string
create_administrative_permission_api_request_adm_instance = CreateAdministrativePermissionAPIRequestADM.from_json(json)
# print the JSON string representation of the object
print(CreateAdministrativePermissionAPIRequestADM.to_json())

# convert the object into a dict
create_administrative_permission_api_request_adm_dict = create_administrative_permission_api_request_adm_instance.to_dict()
# create an instance of CreateAdministrativePermissionAPIRequestADM from a dict
create_administrative_permission_api_request_adm_from_dict = CreateAdministrativePermissionAPIRequestADM.from_dict(create_administrative_permission_api_request_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


