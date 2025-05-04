# GroupCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**GroupIri**](GroupIri.md) |  | [optional] 
**name** | [**GroupName**](GroupName.md) |  | 
**descriptions** | [**GroupDescriptions**](GroupDescriptions.md) |  | 
**project** | [**ProjectIri**](ProjectIri.md) |  | 
**status** | [**GroupStatus**](GroupStatus.md) |  | 
**selfjoin** | [**GroupSelfJoin**](GroupSelfJoin.md) |  | 

## Example

```python
from openapi_client.models.group_create_request import GroupCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GroupCreateRequest from a JSON string
group_create_request_instance = GroupCreateRequest.from_json(json)
# print the JSON string representation of the object
print(GroupCreateRequest.to_json())

# convert the object into a dict
group_create_request_dict = group_create_request_instance.to_dict()
# create an instance of GroupCreateRequest from a dict
group_create_request_from_dict = GroupCreateRequest.from_dict(group_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


