# ListChangeCommentsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comments** | [**Comments**](Comments.md) |  | 

## Example

```python
from openapi_client.models.list_change_comments_request import ListChangeCommentsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ListChangeCommentsRequest from a JSON string
list_change_comments_request_instance = ListChangeCommentsRequest.from_json(json)
# print the JSON string representation of the object
print(ListChangeCommentsRequest.to_json())

# convert the object into a dict
list_change_comments_request_dict = list_change_comments_request_instance.to_dict()
# create an instance of ListChangeCommentsRequest from a dict
list_change_comments_request_from_dict = ListChangeCommentsRequest.from_dict(list_change_comments_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


