# ListChangeLabelsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**labels** | [**Labels**](Labels.md) |  | 

## Example

```python
from openapi_client.models.list_change_labels_request import ListChangeLabelsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ListChangeLabelsRequest from a JSON string
list_change_labels_request_instance = ListChangeLabelsRequest.from_json(json)
# print the JSON string representation of the object
print(ListChangeLabelsRequest.to_json())

# convert the object into a dict
list_change_labels_request_dict = list_change_labels_request_instance.to_dict()
# create an instance of ListChangeLabelsRequest from a dict
list_change_labels_request_from_dict = ListChangeLabelsRequest.from_dict(list_change_labels_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


