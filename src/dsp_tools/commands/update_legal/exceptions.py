from dsp_tools.error.exceptions import UserError


class InvalidLicenseError(UserError):
    """This error is raised when a license string cannot be parsed."""

    license_str: str

    def __init__(self, license_str: str) -> None:
        msg = (
            f"The provided license string is invalid and cannot be parsed: '{license_str}'"
            "You must provide a license that can be parsed by xmllib.find_license_in_string(). "
            "See https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/general-functions/#xmllib.general_functions.find_license_in_string"
        )
        super().__init__(msg)
