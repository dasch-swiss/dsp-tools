# PermissionCodeAndProjectRestrictedViewSettings


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**permission_code** | **int** |  | 
**restricted_view_settings** | [**ProjectRestrictedViewSettingsADM**](ProjectRestrictedViewSettingsADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.permission_code_and_project_restricted_view_settings import PermissionCodeAndProjectRestrictedViewSettings

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionCodeAndProjectRestrictedViewSettings from a JSON string
permission_code_and_project_restricted_view_settings_instance = PermissionCodeAndProjectRestrictedViewSettings.from_json(json)
# print the JSON string representation of the object
print(PermissionCodeAndProjectRestrictedViewSettings.to_json())

# convert the object into a dict
permission_code_and_project_restricted_view_settings_dict = permission_code_and_project_restricted_view_settings_instance.to_dict()
# create an instance of PermissionCodeAndProjectRestrictedViewSettings from a dict
permission_code_and_project_restricted_view_settings_from_dict = PermissionCodeAndProjectRestrictedViewSettings.from_dict(permission_code_and_project_restricted_view_settings_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


