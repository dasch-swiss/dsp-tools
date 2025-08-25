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
    
    # Ensure consistent dtypes before concatenation
    first_row_data = {
        "Run": [0], 
        "Timestamp": [None], 
        "DB_Before": [0.0], 
        "DB_After": [0.0]
    }
    first_row = pd.DataFrame(first_row_data)
    
    # Convert dtypes to match the main DataFrame
    for col in df.columns:
        if col in first_row.columns:
            first_row[col] = first_row[col].astype(df[col].dtype)
    
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

    unique_types = df["val_type"].unique()
    colors = plt.cm.tab10(range(len(unique_types)))
    
    # Create two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: DB Size vs Number of Values (one line per val_type)
    for i, val_type in enumerate(unique_types):
        type_data = df[df["val_type"] == val_type].sort_values("val_num")
        ax1.plot(type_data["val_num"], type_data["DB_After"], 
                marker='o', color=colors[i], label=val_type, linewidth=2)
    
    ax1.set_xlabel("Number of Values")
    ax1.set_ylabel("DB Size After (GB)")
    ax1.set_title("Database Size vs Number of Values")
    ax1.grid(True, alpha=0.3)
    ax1.legend(title="Value Type")
    
    # Plot 2: DB Size vs Number of Resources (one line per val_type)
    for i, val_type in enumerate(unique_types):
        type_data = df[df["val_type"] == val_type].sort_values("res_num")
        ax2.plot(type_data["res_num"], type_data["DB_After"], 
                marker='o', color=colors[i], label=val_type, linewidth=2)
    
    ax2.set_xlabel("Number of Resources")
    ax2.set_ylabel("DB Size After (GB)")
    ax2.set_title("Database Size vs Number of Resources")
    ax2.grid(True, alpha=0.3)
    ax2.legend(title="Value Type")

    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/val_res_num_increasing_scatterplot.png")
    plt.close()


prepare_fuseki_multiple_uploads()
prepare_val_res_num_increasing()
prepare_fuseki_size_value_comparison()
