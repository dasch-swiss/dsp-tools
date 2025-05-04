# GroupStatusUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**GroupStatus**](GroupStatus.md) |  | 

## Example

```python
from openapi_client.models.group_status_update_request import GroupStatusUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GroupStatusUpdateRequest from a JSON string
group_status_update_request_instance = GroupStatusUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(GroupStatusUpdateRequest.to_json())

# convert the object into a dict
group_status_update_request_dict = group_status_update_request_instance.to_dict()
# create an instance of GroupStatusUpdateRequest from a dict
group_status_update_request_from_dict = GroupStatusUpdateRequest.from_dict(group_status_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


