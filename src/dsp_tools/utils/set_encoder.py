import json
from typing import Any
from typing import Union

from dsp_tools.commands.project.models.context import Context
from dsp_tools.commands.project.models.helpers import OntoIri


class SetEncoder(json.JSONEncoder):
    """Encoder used to serialize objects to JSON that would by default not be serializable"""

    def default(self, o: Union[set[Any], Context, OntoIri]) -> Any:
        """Return a serializable object for o"""
        if isinstance(o, set):
            return list(o)
        elif isinstance(o, Context):
            return o.toJsonObj()
        elif isinstance(o, OntoIri):
            return {"iri": o.iri, "hashtag": o.hashtag}
        return json.JSONEncoder.default(self, o)
