# BasicUserInformationChangeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | [**Username**](Username.md) |  | [optional] 
**email** | [**Email**](Email.md) |  | [optional] 
**given_name** | [**GivenName**](GivenName.md) |  | [optional] 
**family_name** | [**FamilyName**](FamilyName.md) |  | [optional] 
**lang** | [**LanguageCode**](LanguageCode.md) |  | [optional] 

## Example

```python
from openapi_client.models.basic_user_information_change_request import BasicUserInformationChangeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BasicUserInformationChangeRequest from a JSON string
basic_user_information_change_request_instance = BasicUserInformationChangeRequest.from_json(json)
# print the JSON string representation of the object
print(BasicUserInformationChangeRequest.to_json())

# convert the object into a dict
basic_user_information_change_request_dict = basic_user_information_change_request_instance.to_dict()
# create an instance of BasicUserInformationChangeRequest from a dict
basic_user_information_change_request_from_dict = BasicUserInformationChangeRequest.from_dict(basic_user_information_change_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


