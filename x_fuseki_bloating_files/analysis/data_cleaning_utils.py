import pandas as pd
import regex


def clean_db_sizes(df: pd.DataFrame) -> pd.DataFrame:
    def convert_input(size: str) -> float:
        if size.endswith("M"):
            return 0.0
        if not size.endswith("G"):
            raise ValueError(f"Unknown ending for size: {size}")
        return float(size.rstrip("G"))

    df["DB_Before"] = df["DB_Before"].apply(convert_input)
    df["DB_After"] = df["DB_After"].apply(convert_input)
    return df


def add_filename_info_to_df(df: pd.DataFrame, filename_col: str) -> pd.DataFrame:
    info_data = []
    for filename in df[filename_col]:
        info_dict = _get_info_from_filename(filename)
        info_data.append(info_dict)

    info_df = pd.DataFrame(info_data)
    result_df = pd.concat([df, info_df], axis=1)
    return result_df


def _get_info_from_filename(filename: str) -> dict[str, str | int | None]:
    f_patt = r"^^res-(.*)_val-(.*?)_(.*).xml$"
    found = regex.search(f_patt, filename)
    if found:
        return {"res_num": int(found.group(1)), "val_num": int(found.group(2)), "val_type": found.group(3)}
    f_no_vals = r"^res-(.*)_val-(.*).xml$"
    found = regex.search(f_no_vals, filename)
    if found:
        return {"res_num": int(found.group(1)), "val_num": int(found.group(2)), "val_type": "No values"}
    raise ValueError(f"Unknown file pattern: {filename}")
