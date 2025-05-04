# PagedResponseAuthorship


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | **List[str]** |  | 
**pagination** | [**Pagination**](Pagination.md) |  | 

## Example

```python
from openapi_client.models.paged_response_authorship import PagedResponseAuthorship

# TODO update the JSON string below
json = "{}"
# create an instance of PagedResponseAuthorship from a JSON string
paged_response_authorship_instance = PagedResponseAuthorship.from_json(json)
# print the JSON string representation of the object
print(PagedResponseAuthorship.to_json())

# convert the object into a dict
paged_response_authorship_dict = paged_response_authorship_instance.to_dict()
# create an instance of PagedResponseAuthorship from a dict
paged_response_authorship_from_dict = PagedResponseAuthorship.from_dict(paged_response_authorship_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


