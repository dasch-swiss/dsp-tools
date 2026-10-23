import re

# Resources of the combined 9999 failing data that the dsp-api transformer rejects before the SHACL validation.
# One of them in a payload stops the whole import.
TRANSFORMER_REJECTED_BASE_IDS = frozenset(
    f"content_violation__{x}"
    for x in (
        "date_end_day_does_not_exist",
        "date_end_month_does_not_exist",
        "date_range_first_is_ce_second_bce",
        "date_range_wrong_mixed_precision",
        "date_range_wrong_year_full_GREGORIAN",
        "date_range_wrong_year_full_ISLAMIC",
        "date_range_wrong_year_full_JULIAN",
        "date_range_wrong_year_good_month_wrong",
        "date_range_wrong_year_month_good_day_wrong",
        "date_range_wrong_yyyy",
        "date_range_wrong_yyyy_mm",
        "date_single_month_does_not_exist",
        "geolocation_lv03_number_as_lv95",
        "geolocation_out_of_range",
        "geolocation_wrong_pair",
    )
)
_COPY_SUFFIX = re.compile(r"__[ce]\d{6}$")


def get_base_id(res_id: str) -> str:
    return _COPY_SUFFIX.sub("", res_id)


def get_transformer_rejected_ids(res_ids: list[str]) -> set[str]:
    return {x for x in res_ids if get_base_id(x) in TRANSFORMER_REJECTED_BASE_IDS}
