# NotFoundException


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** |  | 

## Example

```python
from openapi_client.models.not_found_exception import NotFoundException

# TODO update the JSON string below
json = "{}"
# create an instance of NotFoundException from a JSON string
not_found_exception_instance = NotFoundException.from_json(json)
# print the JSON string representation of the object
print(NotFoundException.to_json())

# convert the object into a dict
not_found_exception_dict = not_found_exception_instance.to_dict()
# create an instance of NotFoundException from a dict
not_found_exception_from_dict = NotFoundException.from_dict(not_found_exception_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


