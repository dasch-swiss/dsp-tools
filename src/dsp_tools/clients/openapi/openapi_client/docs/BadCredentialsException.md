# BadCredentialsException


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** |  | 

## Example

```python
from openapi_client.models.bad_credentials_exception import BadCredentialsException

# TODO update the JSON string below
json = "{}"
# create an instance of BadCredentialsException from a JSON string
bad_credentials_exception_instance = BadCredentialsException.from_json(json)
# print the JSON string representation of the object
print(BadCredentialsException.to_json())

# convert the object into a dict
bad_credentials_exception_dict = bad_credentials_exception_instance.to_dict()
# create an instance of BadCredentialsException from a dict
bad_credentials_exception_from_dict = BadCredentialsException.from_dict(bad_credentials_exception_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


