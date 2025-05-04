# ProjectAdminMembersGetResponseADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**members** | [**List[UserDto]**](UserDto.md) |  | [optional] 

## Example

```python
from openapi_client.models.project_admin_members_get_response_adm import ProjectAdminMembersGetResponseADM

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectAdminMembersGetResponseADM from a JSON string
project_admin_members_get_response_adm_instance = ProjectAdminMembersGetResponseADM.from_json(json)
# print the JSON string representation of the object
print(ProjectAdminMembersGetResponseADM.to_json())

# convert the object into a dict
project_admin_members_get_response_adm_dict = project_admin_members_get_response_adm_instance.to_dict()
# create an instance of ProjectAdminMembersGetResponseADM from a dict
project_admin_members_get_response_adm_from_dict = ProjectAdminMembersGetResponseADM.from_dict(project_admin_members_get_response_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


