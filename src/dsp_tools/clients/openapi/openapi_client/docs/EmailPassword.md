# EmailPassword


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | [**Email**](Email.md) |  | 
**password** | **str** |  | 

## Example

```python
from openapi_client.models.email_password import EmailPassword

# TODO update the JSON string below
json = "{}"
# create an instance of EmailPassword from a JSON string
email_password_instance = EmailPassword.from_json(json)
# print the JSON string representation of the object
print(EmailPassword.to_json())

# convert the object into a dict
email_password_dict = email_password_instance.to_dict()
# create an instance of EmailPassword from a dict
email_password_from_dict = EmailPassword.from_dict(email_password_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


