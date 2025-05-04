# PasswordChangeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**requester_password** | [**Password**](Password.md) |  | 
**new_password** | [**Password**](Password.md) |  | 

## Example

```python
from openapi_client.models.password_change_request import PasswordChangeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PasswordChangeRequest from a JSON string
password_change_request_instance = PasswordChangeRequest.from_json(json)
# print the JSON string representation of the object
print(PasswordChangeRequest.to_json())

# convert the object into a dict
password_change_request_dict = password_change_request_instance.to_dict()
# create an instance of PasswordChangeRequest from a dict
password_change_request_from_dict = PasswordChangeRequest.from_dict(password_change_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


