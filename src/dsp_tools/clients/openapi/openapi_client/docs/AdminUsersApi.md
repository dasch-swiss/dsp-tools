# openapi_client.AdminUsersApi

All URIs are relative to *https://api.dasch.swiss:443*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_admin_users_iri_useriri**](AdminUsersApi.md#delete_admin_users_iri_useriri) | **DELETE** /admin/users/iri/{userIri} | 
[**delete_admin_users_iri_useriri_group_memberships_groupiri**](AdminUsersApi.md#delete_admin_users_iri_useriri_group_memberships_groupiri) | **DELETE** /admin/users/iri/{userIri}/group-memberships/{groupIri} | 
[**delete_admin_users_iri_useriri_project_admin_memberships_projectiri**](AdminUsersApi.md#delete_admin_users_iri_useriri_project_admin_memberships_projectiri) | **DELETE** /admin/users/iri/{userIri}/project-admin-memberships/{projectIri} | 
[**delete_admin_users_iri_useriri_project_memberships_projectiri**](AdminUsersApi.md#delete_admin_users_iri_useriri_project_memberships_projectiri) | **DELETE** /admin/users/iri/{userIri}/project-memberships/{projectIri} | 
[**get_admin_users**](AdminUsersApi.md#get_admin_users) | **GET** /admin/users | 
[**get_admin_users_email_email**](AdminUsersApi.md#get_admin_users_email_email) | **GET** /admin/users/email/{email} | 
[**get_admin_users_iri_useriri**](AdminUsersApi.md#get_admin_users_iri_useriri) | **GET** /admin/users/iri/{userIri} | 
[**get_admin_users_iri_useriri_group_memberships**](AdminUsersApi.md#get_admin_users_iri_useriri_group_memberships) | **GET** /admin/users/iri/{userIri}/group-memberships | 
[**get_admin_users_iri_useriri_project_admin_memberships**](AdminUsersApi.md#get_admin_users_iri_useriri_project_admin_memberships) | **GET** /admin/users/iri/{userIri}/project-admin-memberships | 
[**get_admin_users_iri_useriri_project_memberships**](AdminUsersApi.md#get_admin_users_iri_useriri_project_memberships) | **GET** /admin/users/iri/{userIri}/project-memberships | 
[**get_admin_users_username_username**](AdminUsersApi.md#get_admin_users_username_username) | **GET** /admin/users/username/{username} | 
[**post_admin_users**](AdminUsersApi.md#post_admin_users) | **POST** /admin/users | 
[**post_admin_users_iri_useriri_group_memberships_groupiri**](AdminUsersApi.md#post_admin_users_iri_useriri_group_memberships_groupiri) | **POST** /admin/users/iri/{userIri}/group-memberships/{groupIri} | 
[**post_admin_users_iri_useriri_project_admin_memberships_projectiri**](AdminUsersApi.md#post_admin_users_iri_useriri_project_admin_memberships_projectiri) | **POST** /admin/users/iri/{userIri}/project-admin-memberships/{projectIri} | 
[**post_admin_users_iri_useriri_project_memberships_projectiri**](AdminUsersApi.md#post_admin_users_iri_useriri_project_memberships_projectiri) | **POST** /admin/users/iri/{userIri}/project-memberships/{projectIri} | 
[**put_admin_users_iri_useriri_basicuserinformation**](AdminUsersApi.md#put_admin_users_iri_useriri_basicuserinformation) | **PUT** /admin/users/iri/{userIri}/BasicUserInformation | 
[**put_admin_users_iri_useriri_password**](AdminUsersApi.md#put_admin_users_iri_useriri_password) | **PUT** /admin/users/iri/{userIri}/Password | 
[**put_admin_users_iri_useriri_status**](AdminUsersApi.md#put_admin_users_iri_useriri_status) | **PUT** /admin/users/iri/{userIri}/Status | 
[**put_admin_users_iri_useriri_systemadmin**](AdminUsersApi.md#put_admin_users_iri_useriri_systemadmin) | **PUT** /admin/users/iri/{userIri}/SystemAdmin | 


# **delete_admin_users_iri_useriri**
> UserResponse delete_admin_users_iri_useriri(user_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Delete a user identified by IRI (change status to false).

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_users_iri_useriri(user_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->delete_admin_users_iri_useriri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->delete_admin_users_iri_useriri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_admin_users_iri_useriri_group_memberships_groupiri**
> UserResponse delete_admin_users_iri_useriri_group_memberships_groupiri(user_iri, group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Remove a user form an group membership identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    group_iri = 'http://rdfh.ch/groups/0042/a95UWs71KUklnFOe1rcw1w' # str | The IRI of a group. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_users_iri_useriri_group_memberships_groupiri(user_iri, group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->delete_admin_users_iri_useriri_group_memberships_groupiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->delete_admin_users_iri_useriri_group_memberships_groupiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **group_iri** | **str**| The IRI of a group. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_admin_users_iri_useriri_project_admin_memberships_projectiri**
> UserResponse delete_admin_users_iri_useriri_project_admin_memberships_projectiri(user_iri, project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Remove a user form an admin project membership identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_users_iri_useriri_project_admin_memberships_projectiri(user_iri, project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->delete_admin_users_iri_useriri_project_admin_memberships_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->delete_admin_users_iri_useriri_project_admin_memberships_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_admin_users_iri_useriri_project_memberships_projectiri**
> UserResponse delete_admin_users_iri_useriri_project_memberships_projectiri(user_iri, project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Remove a user from a project membership identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.delete_admin_users_iri_useriri_project_memberships_projectiri(user_iri, project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->delete_admin_users_iri_useriri_project_memberships_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->delete_admin_users_iri_useriri_project_memberships_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_users**
> UsersResponse get_admin_users(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns all users.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.users_response import UsersResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_users(knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->get_admin_users:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->get_admin_users: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UsersResponse**](UsersResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_users_email_email**
> UserResponse get_admin_users_email_email(email, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns a user identified by their Email.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    email = 'jane@example.com' # str | The user email. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_users_email_email(email, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->get_admin_users_email_email:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->get_admin_users_email_email: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email** | **str**| The user email. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_users_iri_useriri**
> UserResponse get_admin_users_iri_useriri(user_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns a user identified by their IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_users_iri_useriri(user_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->get_admin_users_iri_useriri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->get_admin_users_iri_useriri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_users_iri_useriri_group_memberships**
> UserGroupMembershipsGetResponseADM get_admin_users_iri_useriri_group_memberships(user_iri)

Returns the user's group memberships for a user identified by their IRI.

### Example


```python
import openapi_client
from openapi_client.models.user_group_memberships_get_response_adm import UserGroupMembershipsGetResponseADM
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.

    try:
        api_response = api_instance.get_admin_users_iri_useriri_group_memberships(user_iri)
        print("The response of AdminUsersApi->get_admin_users_iri_useriri_group_memberships:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->get_admin_users_iri_useriri_group_memberships: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 

### Return type

[**UserGroupMembershipsGetResponseADM**](UserGroupMembershipsGetResponseADM.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_users_iri_useriri_project_admin_memberships**
> UserProjectAdminMembershipsGetResponseADM get_admin_users_iri_useriri_project_admin_memberships(user_iri)

Returns the user's project admin memberships for a user identified by their IRI.

### Example


```python
import openapi_client
from openapi_client.models.user_project_admin_memberships_get_response_adm import UserProjectAdminMembershipsGetResponseADM
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.

    try:
        api_response = api_instance.get_admin_users_iri_useriri_project_admin_memberships(user_iri)
        print("The response of AdminUsersApi->get_admin_users_iri_useriri_project_admin_memberships:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->get_admin_users_iri_useriri_project_admin_memberships: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 

### Return type

[**UserProjectAdminMembershipsGetResponseADM**](UserProjectAdminMembershipsGetResponseADM.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_users_iri_useriri_project_memberships**
> UserProjectMembershipsGetResponseADM get_admin_users_iri_useriri_project_memberships(user_iri)

Returns the user's project memberships for a user identified by their IRI.

### Example


```python
import openapi_client
from openapi_client.models.user_project_memberships_get_response_adm import UserProjectMembershipsGetResponseADM
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.

    try:
        api_response = api_instance.get_admin_users_iri_useriri_project_memberships(user_iri)
        print("The response of AdminUsersApi->get_admin_users_iri_useriri_project_memberships:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->get_admin_users_iri_useriri_project_memberships: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 

### Return type

[**UserProjectMembershipsGetResponseADM**](UserProjectMembershipsGetResponseADM.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_admin_users_username_username**
> UserResponse get_admin_users_username_username(username, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Returns a user identified by their Username.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    username = 'JaneDoe' # str | The user name. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.get_admin_users_username_username(username, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->get_admin_users_username_username:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->get_admin_users_username_username: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**| The user name. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_admin_users**
> UserResponse post_admin_users(user_create_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Create a new user.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_create_request import UserCreateRequest
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_create_request = openapi_client.UserCreateRequest() # UserCreateRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_users(user_create_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->post_admin_users:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->post_admin_users: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_create_request** | [**UserCreateRequest**](UserCreateRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_admin_users_iri_useriri_group_memberships_groupiri**
> UserResponse post_admin_users_iri_useriri_group_memberships_groupiri(user_iri, group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Add a user to a group identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    group_iri = 'http://rdfh.ch/groups/0042/a95UWs71KUklnFOe1rcw1w' # str | The IRI of a group. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_users_iri_useriri_group_memberships_groupiri(user_iri, group_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->post_admin_users_iri_useriri_group_memberships_groupiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->post_admin_users_iri_useriri_group_memberships_groupiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **group_iri** | **str**| The IRI of a group. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_admin_users_iri_useriri_project_admin_memberships_projectiri**
> UserResponse post_admin_users_iri_useriri_project_admin_memberships_projectiri(user_iri, project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Add a user as an admin to a project identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_users_iri_useriri_project_admin_memberships_projectiri(user_iri, project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->post_admin_users_iri_useriri_project_admin_memberships_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->post_admin_users_iri_useriri_project_admin_memberships_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_admin_users_iri_useriri_project_memberships_projectiri**
> UserResponse post_admin_users_iri_useriri_project_memberships_projectiri(user_iri, project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Add a user to a project identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    project_iri = 'http://rdfh.ch/projects/0001' # str | The IRI of a project. Must be URL-encoded.
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.post_admin_users_iri_useriri_project_memberships_projectiri(user_iri, project_iri, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->post_admin_users_iri_useriri_project_memberships_projectiri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->post_admin_users_iri_useriri_project_memberships_projectiri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **project_iri** | **str**| The IRI of a project. Must be URL-encoded. | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_admin_users_iri_useriri_basicuserinformation**
> UserResponse put_admin_users_iri_useriri_basicuserinformation(user_iri, basic_user_information_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Update a user's basic information identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.basic_user_information_change_request import BasicUserInformationChangeRequest
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    basic_user_information_change_request = openapi_client.BasicUserInformationChangeRequest() # BasicUserInformationChangeRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_users_iri_useriri_basicuserinformation(user_iri, basic_user_information_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->put_admin_users_iri_useriri_basicuserinformation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->put_admin_users_iri_useriri_basicuserinformation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **basic_user_information_change_request** | [**BasicUserInformationChangeRequest**](BasicUserInformationChangeRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_admin_users_iri_useriri_password**
> UserResponse put_admin_users_iri_useriri_password(user_iri, password_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Change a user's password identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.password_change_request import PasswordChangeRequest
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    password_change_request = openapi_client.PasswordChangeRequest() # PasswordChangeRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_users_iri_useriri_password(user_iri, password_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->put_admin_users_iri_useriri_password:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->put_admin_users_iri_useriri_password: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **password_change_request** | [**PasswordChangeRequest**](PasswordChangeRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_admin_users_iri_useriri_status**
> UserResponse put_admin_users_iri_useriri_status(user_iri, status_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Change a user's status identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.status_change_request import StatusChangeRequest
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    status_change_request = openapi_client.StatusChangeRequest() # StatusChangeRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_users_iri_useriri_status(user_iri, status_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->put_admin_users_iri_useriri_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->put_admin_users_iri_useriri_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **status_change_request** | [**StatusChangeRequest**](StatusChangeRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_admin_users_iri_useriri_systemadmin**
> UserResponse put_admin_users_iri_useriri_systemadmin(user_iri, system_admin_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)

Change a user's SystemAdmin status identified by IRI.

### Example

* Basic Authentication (httpAuth1):
* Bearer Authentication (httpAuth):

```python
import openapi_client
from openapi_client.models.system_admin_change_request import SystemAdminChangeRequest
from openapi_client.models.user_response import UserResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.dasch.swiss:443
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.dasch.swiss:443"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: httpAuth1
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure Bearer authorization: httpAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AdminUsersApi(api_client)
    user_iri = 'http://rdfh.ch/users/1A6c1kfJQLG9C0tQkZA_Ew' # str | The user IRI. Must be URL-encoded.
    system_admin_change_request = openapi_client.SystemAdminChangeRequest() # SystemAdminChangeRequest | 
    knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9 = 'knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9_example' # str |  (optional)

    try:
        api_response = api_instance.put_admin_users_iri_useriri_systemadmin(user_iri, system_admin_change_request, knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9=knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9)
        print("The response of AdminUsersApi->put_admin_users_iri_useriri_systemadmin:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminUsersApi->put_admin_users_iri_useriri_systemadmin: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_iri** | **str**| The user IRI. Must be URL-encoded. | 
 **system_admin_change_request** | [**SystemAdminChangeRequest**](SystemAdminChangeRequest.md)|  | 
 **knora_authentication_mfygsltemfzwg2_boon3_ws43_thi2_dimy9** | **str**|  | [optional] 

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

[httpAuth1](../README.md#httpAuth1), [httpAuth](../README.md#httpAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**401** |  |  -  |
**403** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

