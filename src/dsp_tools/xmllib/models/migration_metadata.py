import warnings
from dataclasses import dataclass

from typing_extensions import deprecated

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib.value_checkers import is_dsp_ark
from dsp_tools.xmllib.value_checkers import is_dsp_iri
from dsp_tools.xmllib.value_checkers import is_timestamp

LIST_SEPARATOR = "\n    - "


@dataclass
class MigrationMetadata:
    """
    Metadata originating from a SALSAH migration.
    This will be deprecated in the future when all projects are migrated.
    """

    creation_date: str | None
    iri: str | None
    ark: str | None
    res_id: str

    @deprecated("This is for salsah migration only and will be deleted in future releases.")
    def __post_init__(self) -> None:
        msg_list = []
        if self.creation_date and not is_timestamp(self.creation_date):
            msg_list.append(f"The value for creation date is not a valid timestamp: {self.creation_date}")
        if self.iri and not is_dsp_iri(self.iri):
            msg_list.append(f"The provided IRI is not valid: {self.iri}")
        if self.ark and not is_dsp_ark(self.ark):
            msg_list.append(f"The provided ARK is not valid: {self.ark}")
        if msg_list:
            msg = (
                f"The migration metadata of the resource with the ID '{self.res_id}' has the following problem(s):"
                f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(msg_list)}"
            )
            warnings.warn(DspToolsUserWarning(msg))

    def as_attrib(self) -> dict[str, str]:
        attrib_dict = {}
        if self.creation_date:
            attrib_dict["creation_date"] = self.creation_date
        if self.iri:
            attrib_dict["iri"] = self.iri
        if self.ark:
            attrib_dict["ark"] = self.ark
        if not attrib_dict:
            msg = (
                f"The metadata of the resource with the ID '{self.res_id}' does not contain any values. "
                f"Please check if an error occurred."
            )
            warnings.warn(DspToolsUserWarning(msg))
        return attrib_dict
