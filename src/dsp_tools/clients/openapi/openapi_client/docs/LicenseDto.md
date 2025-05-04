# LicenseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**uri** | **str** |  | 
**label_en** | **str** |  | 

## Example

```python
from openapi_client.models.license_dto import LicenseDto

# TODO update the JSON string below
json = "{}"
# create an instance of LicenseDto from a JSON string
license_dto_instance = LicenseDto.from_json(json)
# print the JSON string representation of the object
print(LicenseDto.to_json())

# convert the object into a dict
license_dto_dict = license_dto_instance.to_dict()
# create an instance of LicenseDto from a dict
license_dto_from_dict = LicenseDto.from_dict(license_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


