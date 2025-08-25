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

    plt.figure(figsize=(12, 8))
    
    # Create color mapping for val_type
    unique_types = df["val_type"].unique()
    colors = plt.cm.tab10(range(len(unique_types)))
    color_map = {val_type: colors[i] for i, val_type in enumerate(unique_types)}
    bubble_colors = [color_map[val_type] for val_type in df["val_type"]]
    
    scatter = plt.scatter(
        df["res_num"], df["DB_After"], s=df["val_num"] * 10, alpha=0.3, c=bubble_colors
    )
    plt.xlabel("Number of Resources")
    plt.ylabel("DB Size After (GB)")
    plt.title("Database Size by Resource and Value Count")

    # Create legends
    # Color legend for val_type
    color_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map[val_type], 
                               markersize=8, label=val_type) for val_type in unique_types]
    color_legend = plt.legend(handles=color_handles, title="Value Type", loc='upper left', bbox_to_anchor=(1.05, 1))
    
    # Size legend for bubble size
    sizes = [100, 500, 1000]
    size_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
                              markersize=size**0.5/10, label=f"{size} values") for size in sizes]
    size_legend = plt.legend(handles=size_handles, title="Bubble Size", loc='upper left', bbox_to_anchor=(1.05, 0.6))
    
    plt.gca().add_artist(color_legend)

    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/val_res_num_increasing_scatterplot.png")
    plt.close()


prepare_fuseki_multiple_uploads()
prepare_val_res_num_increasing()
prepare_fuseki_size_value_comparison()
