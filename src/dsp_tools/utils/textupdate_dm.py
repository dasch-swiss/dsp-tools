import json
import os
import sys
from datetime import date

unformatted_text_list = ["SimpleText", "Textarea"]
formatted_text_list = ["Richtext"]


def _get_ontologies(data) -> list:
    project = data["project"]
    return project["ontologies"]


def _get_properties(onto) -> dict:
    return onto["properties"]


def change(prop_elem, newValue):
    del prop_elem["gui_element"]
    prop_elem["object"] = newValue


def check_prop_elem(prop_elem):
    gui_element = prop_elem.get("gui_element")

    if gui_element in unformatted_text_list:
        change(prop_elem=prop_elem, newValue="UnformattedTextValue")
    elif gui_element in formatted_text_list:
        change(prop_elem=prop_elem, newValue="FormattedTextValue")


def check_properties(onto):
    properties = _get_properties(onto=onto)
    for i in range(len(properties)):
        prop_elem = properties[i]
        check_prop_elem(prop_elem=prop_elem)


def _check_ontologies(data: dict):
    ontologies = _get_ontologies(data=data)
    for onto in ontologies:
        check_properties(onto=onto)


def get_last_before(path: str) -> [str, str]:
    pos = path.rfind("/")
    last = path
    before = ""
    if pos != -1:
        last = path[pos + 1 :]
        before = path[:pos]

    return last, before


def get_name(last: str) -> str:
    json_str = ".json"
    pos = last.rfind(json_str)
    name = last[:pos]
    return name


def loop_for_valid_path(fix_part: str) -> str:
    json_str = ".json"
    new_path = f"{fix_part}{json_str}"

    count = 1
    while os.path.exists(new_path):
        new_path = f"{fix_part}_{count}{json_str}"
        count += 1
    return new_path


def get_fix_part(before: str, name: str) -> str:
    today = date.today()
    date_ = today.strftime("%Y%m%d")
    fix_part = os.path.join(before, f"{date_}_{name}")
    return fix_part


def create_valid_path(before: str, name: str) -> str:
    fix_part = get_fix_part(before=before, name=name)
    return loop_for_valid_path(fix_part=fix_part)


def get_new_path(path: str) -> str:
    last, before = get_last_before(path=path)
    name = get_name(last=last)
    return create_valid_path(before=before, name=name)


def _write_file(data: dict, path: str):
    new_path = get_new_path(path=path)
    with open(new_path, mode="w", encoding="utf-8") as jsonFile:
        json.dump(data, jsonFile, indent=4, ensure_ascii=False)
    print(f"wrote file to '{new_path}'")


def change_text_values(path: str):
    with open(path, "r", encoding="utf-8") as jsonFile:
        data = json.load(jsonFile)

    _check_ontologies(data=data)
    _write_file(data=data, path=path)
