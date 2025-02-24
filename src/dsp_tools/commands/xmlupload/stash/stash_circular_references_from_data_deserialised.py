from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation


def stash_circular_references(
    resources: list[ResourceDeserialised], stash_lookup: dict[str, list[str]], permission_lookup: dict[str, Permissions]
) -> Stash | None:
    """Stash the values that would create circular references and remove them from the Resources."""


def _process_one_resource(resource: ResourceDeserialised) -> tuple[list[LinkValueStashItem], list[StandoffStashItem]]:
    pass


def _stash_link(
    value: ValueInformation,
    res_id: str,
    res_type: str,
    stash_lookup: dict[str, list[str]],
    permission_lookup: dict[str, Permissions],
) -> LinkValueStashItem | None:
    pass


def _stash_standoff(value: ValueInformation, res_id: str, res_type: str) -> StandoffStashItem | None:
    pass
