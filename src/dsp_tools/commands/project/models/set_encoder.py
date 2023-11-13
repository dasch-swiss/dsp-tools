import json
from typing import Any, Union

from dsp_tools.models.helpers import Context, OntoIri


class SetEncoder(json.JSONEncoder):
    """Encoder used to serialize objects to JSON that would by default not be serializable"""

    def default(self, o: Union[set[Any], Context, OntoIri]) -> Any:
        if isinstance(o, set):
            return list(o)
        elif isinstance(o, Context):
            return o.toJsonObj()
        elif isinstance(o, OntoIri):
            return {"iri": o.iri, "hashtag": o.hashtag}
        return json.JSONEncoder.default(self, o)
