from pathlib import Path

import pandas as pd

from x_fuseki_bloating_files.analysis.data_cleaning_utils import add_filename_info_to_df
from x_fuseki_bloating_files.analysis.data_cleaning_utils import clean_db_sizes

f_dir = Path("x_fuseki_bloating_files/analysis_data")


def prepare_fuseki_multiple_uploads():
    f_path = f_dir / "fuseki_multiple_uploads.csv"
    df = pd.read_csv(f_path)
    df = clean_db_sizes(df)
    first_row = pd.DataFrame({"Run": [0], "Timestamp": [pd.NA], "DB_Before": [pd.NA], "DB_After": [0]})
    df = pd.concat([first_row, df])

    # TODO: lineplot x: "Run" y: "DB_After"
    # TODO: save in x_fuseki_bloating_files/graphics_output


def prepare_fuseki_size_value_comparison() -> None:
    f_path = f_dir / "fuseki_size_value_comparison.csv"
    df = pd.read_csv(f_path)
    df = clean_db_sizes(df)
    df = add_filename_info_to_df(df, "Filename")
    # TODO: calculate average from column "DB_After"
    # TODO: boxplot x: "val_type", y: "DB_After"
    # TODO: add line on x axis that is the average of "DB_After"
    # TODO: save in x_fuseki_bloating_files/graphics_output


def prepare_val_res_num_increasing() -> None:
    f_path = f_dir / "val_res_num_increasing.csv"
    df = pd.read_csv(f_path)
    df = clean_db_sizes(df)
    df = add_filename_info_to_df(df, "Filename")

    # TODO: separate df based on if val_num is consistent or res_num is consistent

    # TODO: df where val_num increases:
    # - scatterplot: x: val_num, y: DB_After
    # TODO: df where res_num increases:
    # -scatterplot: x: res_num, y: DB_After

    # TODO: save in x_fuseki_bloating_files/graphics_output
