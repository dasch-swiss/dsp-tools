from dsp_tools.error.exceptions import UserError


class InvalidMappingConfigFileError(UserError):
    """This error is raised when the provided mapping config file is invalid."""


class OntologyReferencedNotFoundError(UserError):
    def __init__(self, shortcode: str, ontology_name: str) -> None:
        msg = (
            f"The ontology '{ontology_name}' for the project with the shortcode '{shortcode}' "
            f"does not exist on this server."
        )
        super().__init__(msg)
