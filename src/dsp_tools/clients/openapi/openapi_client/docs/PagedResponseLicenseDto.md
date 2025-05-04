# PagedResponseLicenseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[LicenseDto]**](LicenseDto.md) |  | 
**pagination** | [**Pagination**](Pagination.md) |  | 

## Example

```python
from openapi_client.models.paged_response_license_dto import PagedResponseLicenseDto

# TODO update the JSON string below
json = "{}"
# create an instance of PagedResponseLicenseDto from a JSON string
paged_response_license_dto_instance = PagedResponseLicenseDto.from_json(json)
# print the JSON string representation of the object
print(PagedResponseLicenseDto.to_json())

# convert the object into a dict
paged_response_license_dto_dict = paged_response_license_dto_instance.to_dict()
# create an instance of PagedResponseLicenseDto from a dict
paged_response_license_dto_from_dict = PagedResponseLicenseDto.from_dict(paged_response_license_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


