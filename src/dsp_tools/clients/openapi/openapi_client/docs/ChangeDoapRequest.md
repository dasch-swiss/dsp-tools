# ChangeDoapRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**for_group** | **str** |  | [optional] 
**for_resource_class** | **str** |  | [optional] 
**for_property** | **str** |  | [optional] 
**has_permissions** | [**List[PermissionADM]**](PermissionADM.md) |  | [optional] 

## Example

```python
from openapi_client.models.change_doap_request import ChangeDoapRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ChangeDoapRequest from a JSON string
change_doap_request_instance = ChangeDoapRequest.from_json(json)
# print the JSON string representation of the object
print(ChangeDoapRequest.to_json())

# convert the object into a dict
change_doap_request_dict = change_doap_request_instance.to_dict()
# create an instance of ChangeDoapRequest from a dict
change_doap_request_from_dict = ChangeDoapRequest.from_dict(change_doap_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


