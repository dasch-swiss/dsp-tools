from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from x_fuseki_bloating_files.analysis.data_cleaning_utils import add_filename_info_to_df
from x_fuseki_bloating_files.analysis.data_cleaning_utils import clean_db_sizes

f_dir = Path("x_fuseki_bloating_files/analysis_data")


def prepare_fuseki_multiple_uploads():
    f_path = f_dir / "fuseki_multiple_uploads.csv"
    df = pd.read_csv(f_path)
    df = clean_db_sizes(df)
    first_row = pd.DataFrame({"Run": [0], "Timestamp": [None], "DB_Before": [None], "DB_After": [0.0]})
    df = pd.concat([first_row, df], ignore_index=True)

    plt.figure(figsize=(10, 6))
    plt.plot(df["Run"], df["DB_After"], marker="o")
    plt.xlabel("Run")
    plt.ylabel("DB Size After (GB)")
    plt.title("Fuseki Database Size Growth Over Multiple Uploads")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/fuseki_multiple_uploads_lineplot.png")
    plt.close()


def prepare_fuseki_size_value_comparison() -> None:
    f_path = f_dir / "fuseki_size_value_comparison.csv"
    df = pd.read_csv(f_path)
    df = clean_db_sizes(df)
    df = add_filename_info_to_df(df, "Filename")

    avg_db_after = df["DB_After"].mean()

    plt.figure(figsize=(12, 8))
    sns.boxplot(data=df, x="val_type", y="DB_After")
    plt.axhline(y=avg_db_after, color="red", linestyle="--", label=f"Average: {avg_db_after:.2f} GB")
    plt.xlabel("Value Type")
    plt.ylabel("DB Size After (GB)")
    plt.title("Fuseki Database Size by Value Type")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/fuseki_size_value_comparison_boxplot.png")
    plt.close()


def prepare_val_res_num_increasing() -> None:
    f_path = f_dir / "val_res_num_increasing.csv"
    df = pd.read_csv(f_path)
    df = clean_db_sizes(df)
    df = add_filename_info_to_df(df, "Filename")

    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(
        df["res_num"], df["val_num"], s=df["DB_After"] * 100, alpha=0.6, c=df["DB_After"], cmap="viridis"
    )
    plt.xlabel("Number of Resources")
    plt.ylabel("Number of Values")
    plt.title("Database Size by Resource and Value Count")
    plt.colorbar(scatter, label="DB Size After (GB)")

    sizes = [1, 5, 10]
    for size in sizes:
        plt.scatter([], [], s=size * 100, alpha=0.6, c="gray", label=f"{size} GB")
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title="Size")

    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/val_res_num_increasing_scatterplot.png")
    plt.close()


prepare_fuseki_multiple_uploads()
prepare_val_res_num_increasing()
prepare_fuseki_size_value_comparison()
