# Client Pattern Documentation

This document describes the architectural pattern used for client classes in DSP-TOOLS.
These clients provide interfaces to interact with the DSP-API endpoints.

## Overview

The client architecture follows a **Protocol-based dependency injection pattern** that separates interface definitions
from concrete implementations. This design enables testability, modularity, and clear contracts between components.
The clients should be as simple to initiate as possible and be stateless, if possible.

## Core Components

### 1. Protocol Classes (Abstract Interfaces)

Protocol classes define the contract that implementations must follow:

- **Location**: `src/dsp_tools/clients/`
- **Naming**: `<Domain>Client` (e.g., `AuthenticationClient`, `LegalInfoClient`)
- **Implementation**: Use `typing.Protocol` for structural subtyping
- **Purpose**: Define required attributes and method signatures without implementation

Example:

```python
from typing import Protocol


class AuthenticationClient(Protocol):
    server: str
    email: str
    password: str

    def get_token(self) -> str:
        pass
```

### 2. Live Implementations

Live implementations are concrete classes that interact with real DSP API endpoints:

- **Location**: `src/dsp_tools/clients/`
- **Naming**: `<Domain>ClientLive` (e.g., `AuthenticationClientLive`, `LegalInfoClientLive`)
- **Decorator**: Always use `@dataclass` decorator
- **Inheritance**: Inherit from corresponding Protocol class
- **Purpose**: Implement actual HTTP communication with the DSP-API

Example:

```python
from dataclasses import dataclass


@dataclass
class AuthenticationClientLive(AuthenticationClient):
    server: str
    email: str
    password: str
    _token: str | None = None

    def get_token(self) -> str:
        # Implementation here
        pass
```

## Implementation Pattern

### Required Attributes

Live clients typically include:

- **Server identification**: `api_url`
- **Project identification**: `shortcode`, `project_shortcode`, `project_iri`
- **Authentication**: `auth: AuthenticationClient` (for endpoints requiring auth)
- **Private state**: Optional private attributes (e.g., `_token`)

### Request Workflow

There are two main patterns, in some cases the code cannot continue if a request is not successful, see pattern 1.
If the code may continue even if the request is not successful, then `None` will be returned, see pattern 2.

In most cases `HTTPStatus.UNAUTHORIZED` will mean that a `BadCredentialsError` will be raised

Pattern 1: If the request is not successfully, then an error is raised.

```python
def _make_request(self, url: str, data: dict[str, Any] | None = None) -> Response:
    # 1. Prepare request parameters
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.auth.get_token()}",
    }
    params = RequestParameters("POST", url, TIMEOUT, data, headers)

    # 2. Log the request
    log_request(params)

    # 3. Execute request with exception handling
    try:
        response = requests.post(
            url=params.url,
            headers=params.headers,
            data=params.data_serialized,
            timeout=params.timeout,
        )
    except RequestException as err:
        log_and_raise_request_exception(err)

    # 4. Log the response
    log_response(response)

    # 5. Handle response status
    if response.ok:
        return response

    if response.status_code==HTTPStatus.UNAUTHORIZED:
        raise BadCredentialsError("Descriptive error message")

    raise FatalNonOkApiResponseCode(url, response.status_code, response.text)
```

Pattern 2: If the request is not successful, then the user is warned and `None` is returned

```python
def create_resource(self, resource_data: dict[str, Any]) -> str | None:
    # 1. Prepare request parameters
    url = f"{self.api_url}/v2/resources"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.auth.get_token()}",
    }
    params = RequestParameters("POST", url, TIMEOUT, resource_data, headers)

    # 2. Log the request
    log_request(params)

    # 3. Execute request with exception handling
    try:
        response = requests.post(
            url=params.url,
            headers=params.headers,
            data=params.data_serialized,
            timeout=params.timeout,
        )
    except RequestException as err:
        log_and_raise_request_exception(err)

    # 4. Log the response
    log_response(response)

    # 5. Handle response status
    if response.ok:
        result = response.json()
        resource_iri = cast(str, result["@id"])
        return resource_iri

    # 6. Handle specific known error cases
    if response.status_code==HTTPStatus.FORBIDDEN:
        raise BadCredentialsError("You don't have permission to create resources in this project.")

    # 7. Handle unexpected errors non-fatally
    log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
    return None
```

### Key Steps

1. **Prepare Request Parameters**: Create `RequestParameters` object with method, URL, timeout, data, and headers
2. **Log Request**: Call `log_request(params)` before making the request
3. **Execute Request**: Use `requests.<method>()` with explicit parameters wrapped in try/except
4. **Log Response**: Call `log_response(response)` after receiving response
5. **Handle Status**: Check response status and raise appropriate exceptions

### Error Handling Strategy

- **Network errors**: Catch `RequestException` and call `log_and_raise_request_exception(err)`
- **Authentication/Authorization (401/403)**: Raise `BadCredentialsError` with context-specific message
- **Other API errors**: Raise `FatalNonOkApiResponseCode` with URL, status code, and response text
- **Expected failures**: Use `log_and_warn_unexpected_non_ok_response()` when failure is non-fatal

## Common Imports

All live clients typically import:

```python
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, cast

import requests
from loguru import logger
from requests import RequestException, Response

from dsp_tools.clients. < protocol_file >
import < ProtocolClass >
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.error.exceptions import BadCredentialsError, FatalNonOkApiResponseCode
from dsp_tools.utils.request_utils import (
    RequestParameters,
    log_and_raise_request_exception,
    log_request,
    log_response,
)
```

## Constants

- **Timeout values**: Define module-level constants for timeouts (e.g., `TIMEOUT = 60`)
- **Default values**: Use module-level constants for commonly used values

```python
TIMEOUT = 60
```

## Type Safety

- **Type hints**: All parameters, return types, and attributes must have type hints
- **JSON responses**: Use `cast()` when extracting values from JSON responses
- **Optional returns**: Use `| None` for methods that may return None

Example:

```python
def get_token(self) -> str:
    res_json: dict[str, Any] = response.json()
    tkn = cast(str, res_json["token"])
    return tkn
```

## Testing Strategy

- **Mock implementations**: Create mock/fake clients implementing the Protocol for testing
- **Dependency injection**: Pass Protocol types to consumers, not concrete implementations
- **Unittesting**: Test live clients with mocked `requests` library
- **End-to-end testing**: Test against DSP-API in a test container

## Client Dependencies

Clients can depend on other clients (via their Protocol):

```python
@dataclass
class LegalInfoClientLive(LegalInfoClient):
    server: str
    project_shortcode: str
    auth: AuthenticationClient  # Protocol type, not concrete
```

This enables:

- Testing with mock authentication clients
- Flexibility in authentication strategy
- Clear dependency contracts

## Authentication Pattern

Clients requiring authentication:

1. Accept `auth: AuthenticationClient` as an attribute
2. Call `self.auth.get_token()` to get bearer token
3. Include token in `Authorization` header: `f"Bearer {self.auth.get_token()}"`

Example:

```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {self.auth.get_token()}",
}
```

## Best Practices

### DO

- Use `@dataclass` decorator for all live implementations
- Log all requests and responses using provided utilities
- Provide descriptive, actionable error messages
- Create custom Error Classes if it makes sense
- Use module-level constants for timeouts
- Handle specific HTTP status codes with appropriate exceptions
- Type hint all parameters and return values
- Use private methods (prefix with `_`) for internal helpers
- Follow the standardized request workflow

### DON'T

- Skip request/response logging
- Use generic error messages
- Hardcode timeout values in method calls
- Catch exceptions without re-raising or logging
- Return raw response objects from public methods
- Mix business logic with HTTP communication

## Naming Conventions

- **Protocol files**: `<domain>_client.py`
- **Protocol classes**: `<Domain>Client`
- **Implementation files**: `<domain>_client_live.py`
- **Implementation classes**: `<Domain>ClientLive`
- **Private methods**: `_<method_name>`
- **Helper methods**: `_<verb>_and_log_request` for HTTP helpers

## Example: Creating a New Client

First: Define the Protocol in `src/dsp_tools/clients/<domain>_client.py`:

```python
from typing import Protocol


class UserClient(Protocol):
    server: str
    auth: AuthenticationClient

    def get_user(self, user_iri: str) -> dict[str, Any]:
        """Get user information by IRI"""
```

Second: Implement the live client in `src/dsp_tools/clients/<domain>_client_live.py`:

```python
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.user_client import UserClient
from dsp_tools.error.exceptions import BadCredentialsError, FatalNonOkApiResponseCode
from dsp_tools.utils.request_utils import (
    RequestParameters,
    log_and_raise_request_exception,
    log_request,
    log_response,
)

TIMEOUT = 60


@dataclass
class UserClientLive(UserClient):
    server: str
    auth: AuthenticationClient

    def get_user(self, user_iri: str) -> dict[str, Any]:
        url = f"{self.server}/admin/users/{user_iri}"
        headers = {
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        params = RequestParameters("GET", url, TIMEOUT, headers=headers)
        log_request(params)

        try:
            response = requests.get(
                url=params.url,
                headers=params.headers,
                timeout=params.timeout,
            )
        except RequestException as err:
            log_and_raise_request_exception(err)

        log_response(response)

        if response.ok:
            return response.json()

        if response.status_code==HTTPStatus.UNAUTHORIZED:
            raise BadCredentialsError(
                "You don't have permission to access user information."
            )
        raise FatalNonOkApiResponseCode(url, response.status_code, response.text)
```

## Related Documentation

- Request utilities: `src/dsp_tools/utils/request_utils.py`
- Exception definitions: `src/dsp_tools/error/exceptions.py`
- Main project documentation: `/CLAUDE.md`
