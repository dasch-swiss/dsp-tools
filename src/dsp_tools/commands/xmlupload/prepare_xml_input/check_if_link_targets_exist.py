from __future__ import annotations

import regex
from lxml import etree

from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.data_formats.iri_util import is_resource_iri


def check_if_link_targets_exist_root(resources: list[IntermediaryResource]) -> None:
    resptr_errors = _check_if_resptr_targets_exist(resources)
    salsah_errors = _check_if_salsah_targets_exist(resources)
    if errors := resptr_errors + salsah_errors:
        sep = "\n - "
        msg = f"It is not possible to upload the XML file, because it contains invalid links:{sep}{sep.join(errors)}"
        raise InputError(msg)


def check_if_link_targets_exist(resources: list[IntermediaryResource]) -> None:
    res_ids = {x.res_id for x in resources}
    link_value_errors = _check_if_link_value_targets_exist(resources, res_ids)
    salsah_errors = _check_if_standoff_link_targets_exist(resources, res_ids)
    if errors := link_value_errors + salsah_errors:
        sep = "\n - "
        msg = f"It is not possible to upload the XML file, because it contains invalid links:{sep}{sep.join(errors)}"
        raise InputError(msg)


def _check_if_link_value_targets_exist(resources: list[IntermediaryResource], resource_ids: set[str]) -> list[str]:
    not_found = []
    for res in resources:
        for val in res.values:
            if isinstance(val, IntermediaryLink):
                if val.value not in resource_ids:
                    if is_resource_iri(val.value):
                        pass
                    not_found.append(
                        f"Resource '{res.res_id}', property '{val.prop_iri}' has an invalid link target '{val.value}'"
                    )
    return not_found


def _check_if_standoff_link_targets_exist(resources: list[IntermediaryResource], resource_ids: set[str]) -> list[str]:
    not_found = []
    for res in resources:
        for val in res.values:
            if isinstance(val, IntermediaryRichtext):
                missing = [x for x in val.value.find_internal_ids() if x not in resource_ids]
                missing_no_iri = [x for x in missing if not is_resource_iri(x)]
                if missing_no_iri:
                    all_missing = ", ".join(missing_no_iri)
                    not_found.append(
                        f"Resource '{res.res_id}', property '{val.prop_iri}' "
                        f"has a invalid standoff link target(s) '{all_missing}'"
                    )
    return not_found


def _get_resource_ids_from_root(root: etree._Element) -> list[str]:
    resource_tags = ["resource", "link", "region", "video-segment", "audio-segment"]
    return [x.attrib["id"] for x in root.iter() if str(x.tag) in resource_tags]


def _get_id_of_ancestor_resource(invalid_link_val: etree._Element) -> str:
    resource_tags = ["resource", "link", "region", "video-segment", "audio-segment"]
    for tg in resource_tags:
        try:
            res_id = next(invalid_link_val.iterancestors(tag=tg)).attrib["id"]
            return res_id
        except StopIteration:
            pass
    return "Resource ID not found"


def _check_if_resptr_targets_exist(root: etree._Element) -> list[str]:
    link_values = [x for x in root.iter() if x.tag == "resptr"]
    resource_ids = _get_resource_ids_from_root(root)
    invalid_link_values = [x for x in link_values if x.text not in resource_ids]
    invalid_link_values = [x for x in invalid_link_values if not is_resource_iri(str(x.text))]
    errors = []
    for inv in invalid_link_values:
        prop_name = next(inv.iterancestors(tag="resptr-prop")).attrib["name"]
        res_id = _get_id_of_ancestor_resource(inv)
        errors.append(f"Resource '{res_id}', property '{prop_name}' has an invalid link target '{inv.text}'")
    return errors


def _check_if_salsah_targets_exist(root: etree._Element) -> list[str]:
    link_values = [x for x in root.iter() if x.tag == "a"]
    resource_ids = _get_resource_ids_from_root(root)
    invalid_link_values = [x for x in link_values if regex.sub(r"IRI:|:IRI", "", x.attrib["href"]) not in resource_ids]
    invalid_link_values = [x for x in invalid_link_values if x.attrib.get("class") == "salsah-link"]
    invalid_link_values = [x for x in invalid_link_values if not is_resource_iri(x.attrib["href"])]
    errors = []
    for inv in invalid_link_values:
        prop_name = next(inv.iterancestors(tag="text-prop")).attrib["name"]
        res_id = _get_id_of_ancestor_resource(inv)
        errors.append(f"Resource '{res_id}', property '{prop_name}' has an invalid link target '{inv.attrib['href']}'")
    return errors
