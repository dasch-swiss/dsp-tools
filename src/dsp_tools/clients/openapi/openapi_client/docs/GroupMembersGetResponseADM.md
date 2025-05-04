# GroupMembersGetResponseADM


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**members** | [**List[UserDto]**](UserDto.md) |  | [optional] 

## Example

```python
from openapi_client.models.group_members_get_response_adm import GroupMembersGetResponseADM

# TODO update the JSON string below
json = "{}"
# create an instance of GroupMembersGetResponseADM from a JSON string
group_members_get_response_adm_instance = GroupMembersGetResponseADM.from_json(json)
# print the JSON string representation of the object
print(GroupMembersGetResponseADM.to_json())

# convert the object into a dict
group_members_get_response_adm_dict = group_members_get_response_adm_instance.to_dict()
# create an instance of GroupMembersGetResponseADM from a dict
group_members_get_response_adm_from_dict = GroupMembersGetResponseADM.from_dict(group_members_get_response_adm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


