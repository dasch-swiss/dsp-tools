import pandas as pd


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
