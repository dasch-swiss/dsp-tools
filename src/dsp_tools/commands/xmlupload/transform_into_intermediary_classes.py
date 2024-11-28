from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.intermediary.resource import IntermediaryResource
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups


def transform_into_intermediary_classes(
    resources: list[XMLResource], lookups: Lookups
) -> list[IntermediaryResource]: ...
