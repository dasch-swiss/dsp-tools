# SystemAdminChangeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**system_admin** | [**SystemAdmin**](SystemAdmin.md) |  | 

## Example

```python
from openapi_client.models.system_admin_change_request import SystemAdminChangeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SystemAdminChangeRequest from a JSON string
system_admin_change_request_instance = SystemAdminChangeRequest.from_json(json)
# print the JSON string representation of the object
print(SystemAdminChangeRequest.to_json())

# convert the object into a dict
system_admin_change_request_dict = system_admin_change_request_instance.to_dict()
# create an instance of SystemAdminChangeRequest from a dict
system_admin_change_request_from_dict = SystemAdminChangeRequest.from_dict(system_admin_change_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


