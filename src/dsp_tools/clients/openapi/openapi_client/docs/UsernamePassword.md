# UsernamePassword


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | [**Username**](Username.md) |  | 
**password** | **str** |  | 

## Example

```python
from openapi_client.models.username_password import UsernamePassword

# TODO update the JSON string below
json = "{}"
# create an instance of UsernamePassword from a JSON string
username_password_instance = UsernamePassword.from_json(json)
# print the JSON string representation of the object
print(UsernamePassword.to_json())

# convert the object into a dict
username_password_dict = username_password_instance.to_dict()
# create an instance of UsernamePassword from a dict
username_password_from_dict = UsernamePassword.from_dict(username_password_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


