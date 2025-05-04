# IriPassword


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**iri** | [**UserIri**](UserIri.md) |  | 
**password** | **str** |  | 

## Example

```python
from openapi_client.models.iri_password import IriPassword

# TODO update the JSON string below
json = "{}"
# create an instance of IriPassword from a JSON string
iri_password_instance = IriPassword.from_json(json)
# print the JSON string representation of the object
print(IriPassword.to_json())

# convert the object into a dict
iri_password_dict = iri_password_instance.to_dict()
# create an instance of IriPassword from a dict
iri_password_from_dict = IriPassword.from_dict(iri_password_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


