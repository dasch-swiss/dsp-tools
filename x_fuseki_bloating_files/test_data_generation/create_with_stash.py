from typing import TypeVar

from dsp_tools.xmllib import Resource
from dsp_tools.xmllib import create_standoff_link_to_resource
from dsp_tools.xmllib.models.internal.values import Value

T = TypeVar("T", bound=Value)


def _create_one_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"id_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def _create_link_target_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"target_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def _add_richtext(res_1: Resource, res_2: Resource) -> tuple[Resource, Resource]:
    val_1 = create_standoff_link_to_resource(res_2.res_id, "Text")
    res_1.add_richtext(":testRichtext", val_1)
    val_2 = create_standoff_link_to_resource(res_1.res_id, "Text")
    res_2.add_richtext(":testRichtext", val_2)
    return res_1, res_2


def _add_link(res_1: Resource, res_2: Resource) -> tuple[Resource, Resource]:
    res_1.add_link(":testHasLinkTo", res_2.res_id)
    res_2.add_link(":testHasLinkTo", res_1.res_id)
    return res_1, res_2


if __name__ == "__main__":

    def create_link_circles():
        pass

    def create_stand_off_circles():
        pass

    def create_richtext_with_links():
        pass
