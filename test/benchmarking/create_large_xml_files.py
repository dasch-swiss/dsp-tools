from dsp_tools.xmllib import Resource
from dsp_tools.xmllib import XMLRoot

# This is to be used with the ontology: testdata/validate-data/generic/project.json


def add_many_values(res: Resource, number_of_values: int) -> Resource:
    for i in range(number_of_values):
        res.add_integer(prop_name=":testIntegerSimpleText", value=i)
    return res


def add_one_large_text_value(res: Resource, text_length: int) -> Resource:
    txt = "a" * text_length
    return res.add_simpletext(prop_name=":testTextarea", value=txt)


def create_one_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"id_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def create_one_res_many_values(value_counter: int) -> None:
    root = XMLRoot.create_new("9999", "onto")
    res = create_one_resource(0)
    res = add_many_values(res, value_counter)
    root.add_resource(res)
    root.write_file(f"size_test_one_res_with_{value_counter}_values.xml")


def create_one_res_large_text_value(text_length: int) -> None:
    root = XMLRoot.create_new("9999", "onto")
    res = create_one_resource(0)
    res = add_one_large_text_value(res, text_length)
    root.add_resource(res)
    root.write_file(f"size_test_one_res_with_{text_length}_characters_of_text.xml")


def create_many_res_no_values(number_of_resources: int) -> None:
    root = XMLRoot.create_new("9999", "onto")
    resources = [create_one_resource(i) for i in range(number_of_resources)]
    root.add_resource_multiple(resources)
    root.write_file(f"size_test_{number_of_resources}_number_of_resources_no_values.xml")
