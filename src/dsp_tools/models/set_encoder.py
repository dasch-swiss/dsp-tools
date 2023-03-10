import json

from dsp_tools.models.helpers import Context, OntoIri


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Context):
            return obj.toJsonObj()
        elif isinstance(obj, OntoIri):
            return {"iri": obj.iri, "hashtag": obj.hashtag}
        return json.JSONEncoder.default(self, obj)
