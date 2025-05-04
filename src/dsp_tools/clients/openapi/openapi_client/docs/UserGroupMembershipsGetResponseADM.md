# UserGroupMembershipsGetResponseADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**groups** | [**List[Group]**](Group.md) |  | [optional] 

## Example

```python
from openapi_client.models.user_group_memberships_get_response_adm import UserGroupMembershipsGetResponseADM

# TODO update the JSON string below
json = "{}"
# create an instance of UserGroupMembershipsGetResponseADM from a JSON string
user_group_memberships_get_response_adm_instance = UserGroupMembershipsGetResponseADM.from_json(json)
# print the JSON string representation of the object
print(UserGroupMembershipsGetResponseADM.to_json())

# convert the object into a dict
user_group_memberships_get_response_adm_dict = user_group_memberships_get_response_adm_instance.to_dict()
# create an instance of UserGroupMembershipsGetResponseADM from a dict
user_group_memberships_get_response_adm_from_dict = UserGroupMembershipsGetResponseADM.from_dict(user_group_memberships_get_response_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


