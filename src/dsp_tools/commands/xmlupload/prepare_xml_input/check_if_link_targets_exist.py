from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.data_formats.iri_util import is_resource_iri


def check_if_link_targets_exist(resources: list[IntermediaryResource]) -> None:
    res_ids = {x.res_id for x in resources}
    link_value_errors = _check_if_link_value_targets_exist(resources, res_ids)
    standoff_errors = _check_if_standoff_link_targets_exist(resources, res_ids)
    if errors := link_value_errors + standoff_errors:
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
                        f"Resource '{res.res_id}', property '{_clean_prop_iri(val.prop_iri, 'Value')}' "
                        f"has an invalid link target '{val.value}'"
                    )
    return not_found


def _check_if_standoff_link_targets_exist(resources: list[IntermediaryResource], resource_ids: set[str]) -> list[str]:
    not_found = []
    for res in resources:
        for val in res.values:
            if isinstance(val, IntermediaryRichtext):
                missing = [x for x in val.value.find_internal_ids() if x not in resource_ids]
                missing_no_iri = [f"'{x}'" for x in missing if not is_resource_iri(x)]
                if missing_no_iri:
                    all_missing = ", ".join(sorted(missing_no_iri))
                    not_found.append(
                        f"Resource '{res.res_id}', property '{_clean_prop_iri(val.prop_iri)}' "
                        f"has a invalid standoff link target(s) {all_missing}"
                    )
    return not_found


def _clean_prop_iri(iri: str, r_strip: str = "") -> str:
    prop_name = iri.split("/v2#")[-1].rstrip(r_strip)
    prefix = iri.split("/")[-2]
    return f"{prefix}:{prop_name}"
