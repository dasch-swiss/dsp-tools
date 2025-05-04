# UserCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**UserIri**](UserIri.md) |  | [optional] 
**username** | [**Username**](Username.md) |  | 
**email** | [**Email**](Email.md) |  | 
**given_name** | [**GivenName**](GivenName.md) |  | 
**family_name** | [**FamilyName**](FamilyName.md) |  | 
**password** | [**Password**](Password.md) |  | 
**status** | [**UserStatus**](UserStatus.md) |  | 
**lang** | [**LanguageCode**](LanguageCode.md) |  | 
**system_admin** | [**SystemAdmin**](SystemAdmin.md) |  | 

## Example

```python
from openapi_client.models.user_create_request import UserCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UserCreateRequest from a JSON string
user_create_request_instance = UserCreateRequest.from_json(json)
# print the JSON string representation of the object
print(UserCreateRequest.to_json())

# convert the object into a dict
user_create_request_dict = user_create_request_instance.to_dict()
# create an instance of UserCreateRequest from a dict
user_create_request_from_dict = UserCreateRequest.from_dict(user_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


