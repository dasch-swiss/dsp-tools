from dsp_tools import xmllib


def second_level(r: xmllib.Resource) -> xmllib.Resource:
    return r.add_link_multiple(":fromNestedFunction", [])
