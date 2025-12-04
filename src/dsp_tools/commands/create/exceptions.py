from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


class ProjectJsonSchemaValidationError(UserError):
    def __init__(self, detail_msg: str) -> None:
        super().__init__(detail_msg)


class InvalidPermissionsOverruleError(UserError):
    def __init__(self, error_locations: dict[str, str]) -> None:
        err_msg = (
            "All classes in project.default_permissions_overrule.limited_view "
            "must be subclasses of 'StillImageRepresentation', because the 'limited view' "
            "permission is only implemented for images (i.e. blurring, watermarking). \n"
            "In order to check, the classes must be provided in the form \n"
            '    "limited_view": ["ontoname:Classname", ...]\n\n'
            "The following classes do not meet this requirement:\n"
        )
        err_msg += "\n".join(f" - {loc}: {error}" for loc, error in error_locations.items())
        super().__init__(err_msg)


class UndefinedSuperPropertiesError(UserError):
    def __init__(self, error_locations: dict[str, list[str]]) -> None:
        err_msg = "Your data model contains properties that are derived from an invalid super-property:\n"
        err_msg += "\n".join(f" - {loc}: {invalids}" for loc, invalids in error_locations.items())
        super().__init__(err_msg)


class CircularOntologyDependency(UserError):
    """Class if a circular dependency was found in the ontology."""

    def __init__(self, dependency_location: str) -> None:
        msg = (
            f"A circular dependency of {dependency_location} was found in your project. "
            f"It is not possible for an ontology to have circular dependencies."
        )
        super().__init__(msg)


class UnableToCreateProjectError(InternalError):
    """Class if a project cannot be created."""
