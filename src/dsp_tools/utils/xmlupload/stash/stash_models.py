from dataclasses import dataclass

from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource


@dataclass(frozen=True)
class StandoffStashItem:
    """
    A dataclass for a stashed standoff xml.
    """

    uuid: str
    resource: XMLResource
    link_prop: XMLProperty
    value: KnoraStandoffXml
    # Permissions missing still
