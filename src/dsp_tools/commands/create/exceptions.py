from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError

#######
# Input Validation Errors


class ProjectJsonSchemaValidationError(UserError):
    def __init__(self, detail_msg: str) -> None:
        super().__init__(detail_msg)


class CircularOntologyDependency(UserError):
    """Class if a circular dependency was found in the ontology."""

    def __init__(self, dependency_location: str) -> None:
        msg = (
            f"A circular dependency of {dependency_location} was found in your project. "
            f"It is not possible for an ontology to have circular dependencies."
        )
        super().__init__(msg)


#######
# Internal Errors


class UnableToCreateProjectError(InternalError):
    """Class if a project cannot be created."""
