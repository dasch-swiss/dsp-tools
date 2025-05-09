# AggregatedHealth


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**Status**](Status.md) |  | 
**components** | [**Dict[str, Health]**](Health.md) |  | [optional] 

## Example

```python
from openapi_client.models.aggregated_health import AggregatedHealth

# TODO update the JSON string below
json = "{}"
# create an instance of AggregatedHealth from a JSON string
aggregated_health_instance = AggregatedHealth.from_json(json)
# print the JSON string representation of the object
print(AggregatedHealth.to_json())

# convert the object into a dict
aggregated_health_dict = aggregated_health_instance.to_dict()
# create an instance of AggregatedHealth from a dict
aggregated_health_from_dict = AggregatedHealth.from_dict(aggregated_health_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


