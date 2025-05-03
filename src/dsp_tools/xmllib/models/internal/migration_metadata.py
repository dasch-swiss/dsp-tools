from dataclasses import dataclass

from typing_extensions import deprecated

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
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
            msg = f"The migration metadata has the following problem(s):{LIST_SEPARATOR}{LIST_SEPARATOR.join(msg_list)}"
            emit_xmllib_input_warning(MessageInfo(msg, self.res_id))

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
                "The migration metadata of the resource does not contain any values. Please check if an error occurred."
            )
            emit_xmllib_input_warning(MessageInfo(msg, self.res_id))
        return attrib_dict
