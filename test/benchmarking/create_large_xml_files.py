from pathlib import Path

from dsp_tools.xmllib import Resource
from dsp_tools.xmllib import XMLRoot

# This is to be used with the ontology: testdata/validate-data/generic/project.json


def create_one_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"id_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def file_with_many_resources_no_values(res_counter: int, save_dir: Path) -> None:
    root = XMLRoot.create_new("9999", "onto")
    resources = [create_one_resource(i) for i in range(res_counter)]
    root.add_resource_multiple(resources)
    root.write_file(save_dir / f"res-{res_counter}_val-0.xml")


def file_with_many_resources_and_int_values(res_counter: int, value_counter: int, save_dir: Path) -> None:
    root = XMLRoot.create_new("9999", "onto")
    resources = [create_one_resource(i) for i in range(res_counter)]
    resources = [add_many_int_values(res, value_counter) for res in resources]
    root.add_resource_multiple(resources)
    root.write_file(save_dir / f"res-{res_counter}_val-{value_counter}_int_values.xml")


def add_many_int_values(res: Resource, number_of_values: int) -> Resource:
    for i in range(number_of_values):
        res.add_integer(prop_name=":testIntegerSimpleText", value=i)
    return res


def file_with_many_resources_and_decimal_values(res_counter: int, value_counter: int, save_dir: Path) -> None:
    root = XMLRoot.create_new("9999", "onto")
    resources = [create_one_resource(i) for i in range(res_counter)]
    resources = [add_many_int_values(res, value_counter) for res in resources]
    root.add_resource_multiple(resources)
    root.write_file(save_dir / f"res-{res_counter}_val-{value_counter}_decimal_values.xml")


def add_many_float_values(res: Resource, number_of_values: int) -> Resource:
    for i in range(number_of_values):
        res.add_decimal(prop_name=":testDecimalSimpleText", value=i / 10)
    return res


def file_with_many_resources_and_large_text_value(
    res_counter: int, value_counter: int, text_length: int, save_dir: Path
) -> None:
    root = XMLRoot.create_new("9999", "onto")
    resources = [create_one_resource(i) for i in range(res_counter)]
    resources = [add_one_large_text_value(res, text_length) for res in resources]
    root.add_resource_multiple(resources)
    root.write_file(save_dir / f"res-{res_counter}_val-{value_counter}_text-len-{text_length}.xml")


def add_one_large_text_value(res: Resource, text_length: int) -> Resource:
    txt = "a" * text_length
    return res.add_simpletext(prop_name=":testTextarea", value=txt)


if __name__ == "__main__":

    def step_1() -> None:
        save_dir = Path("x_fuseki_bloating_files/files")
        save_dir.mkdir(exist_ok=True)

        def make_all(faktor: int) -> None:
            res_number = 10_000
            res_increased = res_number * faktor
            val_number = 10
            val_increased = val_number * faktor
            text_size = 20_000

            # no values
            file_with_many_resources_no_values(
                res_counter=res_increased,
                save_dir=save_dir,
            )

            # INT
            # res increased
            file_with_many_resources_and_int_values(
                res_counter=res_increased,
                value_counter=val_number,
                save_dir=save_dir,
            )
            # val increased
            file_with_many_resources_and_int_values(
                res_counter=res_number,
                value_counter=val_increased,
                save_dir=save_dir,
            )

            # LARGE TEXT
            # res increased
            file_with_many_resources_and_large_text_value(
                res_counter=res_increased,
                value_counter=val_number,
                text_length=text_size,
                save_dir=save_dir,
            )
            # val increased
            file_with_many_resources_and_large_text_value(
                res_counter=res_number,
                value_counter=val_increased,
                text_length=text_size,
                save_dir=save_dir,
            )

            # SMALL TEXT
            # res increased
            file_with_many_resources_and_large_text_value(
                res_counter=res_increased,
                value_counter=val_number,
                text_length=1,
                save_dir=save_dir,
            )
            # val increased
            file_with_many_resources_and_large_text_value(
                res_counter=res_number,
                value_counter=val_increased,
                text_length=1,
                save_dir=save_dir,
            )

        for i in range(1, 6):
            make_all(i)
