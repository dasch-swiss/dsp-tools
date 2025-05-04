# LogoutResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **int** |  | 
**message** | **str** |  | 

## Example

```python
from openapi_client.models.logout_response import LogoutResponse

# TODO update the JSON string below
json = "{}"
# create an instance of LogoutResponse from a JSON string
logout_response_instance = LogoutResponse.from_json(json)
# print the JSON string representation of the object
print(LogoutResponse.to_json())

# convert the object into a dict
logout_response_dict = logout_response_instance.to_dict()
# create an instance of LogoutResponse from a dict
logout_response_from_dict = LogoutResponse.from_dict(logout_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


