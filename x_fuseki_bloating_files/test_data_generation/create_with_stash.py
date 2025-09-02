from pathlib import Path
from typing import TypeVar

from dsp_tools.xmllib import Resource
from dsp_tools.xmllib import XMLRoot
from dsp_tools.xmllib import create_standoff_link_to_resource
from dsp_tools.xmllib.models.internal.values import Value

# This is to be used with the ontology: testdata/validate-data/generic/project.json

T = TypeVar("T", bound=Value)


def _create_one_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"id_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def _create_link_target_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"target_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def _add_richtext(res_1: Resource, res_2: Resource) -> tuple[Resource, Resource]:
    for _ in range(6):
        val_1 = create_standoff_link_to_resource(res_2.res_id, "Text")
        res_1.add_richtext(":testRichtext", val_1)
        val_2 = create_standoff_link_to_resource(res_1.res_id, "Text")
        res_2.add_richtext(":testRichtext", val_2)
    return res_1, res_2


def _add_link(res_1: Resource, res_2: Resource) -> tuple[Resource, Resource]:
    for _ in range(6):
        res_1.add_link(":testHasLinkTo", res_2.res_id)
        res_2.add_link(":testHasLinkTo", res_1.res_id)
    return res_1, res_2


if __name__ == "__main__":

    def main(total_res: int):
        res_count = int(total_res / 2)
        save_dir = Path("x_fuseki_bloating_files/files")
        save_dir.mkdir(exist_ok=True)

        def create_link_circles():
            root = XMLRoot.create_new("9999", "onto")
            res_1 = [_create_one_resource(i) for i in range(res_count)]
            res_2 = [_create_link_target_resource(i) for i in range(res_count)]
            for r1, r2 in zip(res_1, res_2):
                r = _add_richtext(r1, r2)
                root.add_resource_multiple(r)
            root.write_file(save_dir / f"res-{res_count}_val-12_link_{res_count}-stash.xml")

        def create_stand_off_circles():
            root = XMLRoot.create_new("9999", "onto")
            res_1 = [_create_one_resource(i) for i in range(res_count)]
            res_2 = [_create_link_target_resource(i) for i in range(res_count)]
            for r1, r2 in zip(res_1, res_2):
                r = _add_link(r1, r2)
                root.add_resource_multiple(r)
            root.write_file(save_dir / f"res-{res_count}_val-12_richtext_{res_count}-stash.xml")

        create_link_circles()
        create_stand_off_circles()

    main(10_000)
