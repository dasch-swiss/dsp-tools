# Unhealthy


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**Status**](Status.md) |  | 
**components** | [**Dict[str, Health]**](Health.md) |  | [optional] 

## Example

```python
from openapi_client.models.unhealthy import Unhealthy

# TODO update the JSON string below
json = "{}"
# create an instance of Unhealthy from a JSON string
unhealthy_instance = Unhealthy.from_json(json)
# print the JSON string representation of the object
print(Unhealthy.to_json())

# convert the object into a dict
unhealthy_dict = unhealthy_instance.to_dict()
# create an instance of Unhealthy from a dict
unhealthy_from_dict = Unhealthy.from_dict(unhealthy_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


