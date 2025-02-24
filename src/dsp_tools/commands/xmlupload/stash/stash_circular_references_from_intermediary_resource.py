from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash


def stash_circular_references(
    resources: list[IntermediaryResource], stash_lookup: dict[str, list[str]]
) -> Stash | None:
    """Stash the values that would create circular references and remove them from the Resources."""


def _process_one_resource(
    resource: IntermediaryResource,
    stash_lookup: dict[str, list[str]],
) -> tuple[list[LinkValueStashItem], list[StandoffStashItem]]:
    pass


def _stash_link(
    value: IntermediaryLink,
    res_id: str,
    res_type: str,
    stash_lookup: dict[str, list[str]],
) -> LinkValueStashItem:
    pass


def _stash_standoff(value: IntermediaryRichtext, res_id: str, res_type: str) -> StandoffStashItem | None:
    # It is not necessary to add the permissions to the StandoffStashItem because it is an update request
    # If no new permissions are given during that request, the permissions of the previous value are taken
    pass
