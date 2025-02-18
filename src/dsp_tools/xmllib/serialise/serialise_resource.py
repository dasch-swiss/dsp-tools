from lxml import etree

from dsp_tools.xmllib.constants import AnyResource
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.res import Resource


def serialise_resources(resources: list[AnyResource]) -> etree._Element:
    pass


def _serialise_one_resource(res: AnyResource) -> etree._Element:
    pass


def _serialise_generic_resource(res: Resource) -> etree._Element:
    pass


def _serialise_region(res: RegionResource) -> etree._Element:
    pass


def _serialise_link(res: LinkResource) -> etree._Element:
    pass


def _serialise_segment(res: AudioSegmentResource | VideoSegmentResource, segment_type: str) -> etree._Element:
    pass
