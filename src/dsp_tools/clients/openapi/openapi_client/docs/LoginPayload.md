# LoginPayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | [**Email**](Email.md) |  | 
**password** | **str** |  | 
**iri** | [**UserIri**](UserIri.md) |  | 
**username** | [**Username**](Username.md) |  | 

## Example

```python
from openapi_client.models.login_payload import LoginPayload

# TODO update the JSON string below
json = "{}"
# create an instance of LoginPayload from a JSON string
login_payload_instance = LoginPayload.from_json(json)
# print the JSON string representation of the object
print(LoginPayload.to_json())

# convert the object into a dict
login_payload_dict = login_payload_instance.to_dict()
# create an instance of LoginPayload from a dict
login_payload_from_dict = LoginPayload.from_dict(login_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


