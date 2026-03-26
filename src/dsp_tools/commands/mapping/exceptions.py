from dsp_tools.error.exceptions import UserError


class InvalidMappingConfigFile(UserError):
    """This error is raised when the provided mapping config file is invalid."""
