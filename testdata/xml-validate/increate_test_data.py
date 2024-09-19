from copy import deepcopy

from lxml import etree

from dsp_tools.commands.excel2xml import make_root
from dsp_tools.commands.excel2xml import write_xml
from dsp_tools.utils.xml_utils import parse_xml_file


def increaser(root: etree._Element, counter: int) -> list[etree._Element]:
    out = []
    for ele in root.iterdescendants():
        match ele.tag:
            case "{https://dasch.swiss/schema}resource":
                new = deepcopy(ele)
                new.attrib["id"] = f'{ele.attrib["id"]}_{counter}'
                out.append(new)
            case _:
                pass
    return out


root = parse_xml_file("testdata/xml-validate/poc/data/invalid-data.xml")


r = make_root("9999", "onto")
increase_wrong = 400
for i in range(increase_wrong):
    r.extend(increaser(root, i))
root = parse_xml_file("testdata/xml-validate/poc/data/valid-data.xml")
increase_corr = 400
for i in range(increase_corr):
    r.extend(increaser(root, i))

write_xml(r, f"testdata/xml-validate/poc/data/err-{5*increase_wrong}-corr-{7*increase_corr}.xml")
