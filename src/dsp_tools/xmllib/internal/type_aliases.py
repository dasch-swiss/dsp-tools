from __future__ import annotations

from typing import Union

from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.res import Resource

type AnyResource = Union[Resource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource]
