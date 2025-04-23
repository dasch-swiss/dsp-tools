from dsp_tools import xmllib
from second_playground import second_level


def create_res():
    r = xmllib.Resource.create_new("from_function", "type", "lbl")
    r = r.add_simpletext(":prop", "text")
    r = r.add_simpletext_multiple(":fromFunction", [])
    return second_level(r)


create_res()

r = xmllib.Resource.create_new("no_function", "type", "lbl")
r = r.add_simpletext(":prop", "text")
r = r.add_simpletext_multiple(":outerCall", [])
