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
    pass
    # TODO: add the result from _get_info_from_filename to new columns


def _get_info_from_filename(filename: str) -> dict[str, str | int]:
    f_patt = r"^res-(.*)_val-(.*)_(.*).xml$"
    found = regex.search(f_patt, filename)
    if not found:
        raise ValueError(f"Unknown file pattern: {filename}")
    return {"res_num": int(found.group(1)), "val_num": int(found.group(2)), "val_type": found.group(3)}
