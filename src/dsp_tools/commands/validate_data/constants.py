from rdflib import Namespace

KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
REGION_RESOURCE = KNORA_API_STR + "Region"
LINKOBJ_RESOURCE = KNORA_API_STR + "LinkObj"
VIDEO_SEGMENT_RESOURCE = KNORA_API_STR + "VideoSegment"
AUDIO_SEGMENT_RESOURCE = KNORA_API_STR + "AudioSegment"


DASH = Namespace("http://datashapes.org/dash#")

KNORA_API = Namespace(KNORA_API_STR)
API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")

DATA = Namespace("http://data/")
