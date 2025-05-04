# ValidationException


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**msg** | **str** |  | 

## Example

```python
from openapi_client.models.validation_exception import ValidationException

# TODO update the JSON string below
json = "{}"
# create an instance of ValidationException from a JSON string
validation_exception_instance = ValidationException.from_json(json)
# print the JSON string representation of the object
print(ValidationException.to_json())

# convert the object into a dict
validation_exception_dict = validation_exception_instance.to_dict()
# create an instance of ValidationException from a dict
validation_exception_from_dict = ValidationException.from_dict(validation_exception_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


