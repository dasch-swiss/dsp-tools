# StatusChangeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**UserStatus**](UserStatus.md) |  | 

## Example

```python
from openapi_client.models.status_change_request import StatusChangeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StatusChangeRequest from a JSON string
status_change_request_instance = StatusChangeRequest.from_json(json)
# print the JSON string representation of the object
print(StatusChangeRequest.to_json())

# convert the object into a dict
status_change_request_dict = status_change_request_instance.to_dict()
# create an instance of StatusChangeRequest from a dict
status_change_request_from_dict = StatusChangeRequest.from_dict(status_change_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


