from __future__ import annotations

from typing import TypeAlias
from typing import Union

from dsp_tools.xmllib import AudioSegmentResource
from dsp_tools.xmllib import LinkResource
from dsp_tools.xmllib import RegionResource
from dsp_tools.xmllib import Resource
from dsp_tools.xmllib import VideoSegmentResource

AnyResource: TypeAlias = Union[Resource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource]
