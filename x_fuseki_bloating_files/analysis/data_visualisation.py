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
    first_row_data = {"Run": [0], "Timestamp": [None], "DB_Before": [0.0], "DB_After": [0.0]}
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
    plt.title("Database Size Growth Over Multiple Uploads")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/db_multiple_uploads_lineplot.png")
    plt.close()


def prepare_fuseki_size_value_comparison() -> None:
    f_path = f_dir / "fuseki_size_value_comparison.csv"
    df = pd.read_csv(f_path)
    df = clean_db_sizes(df)
    df = add_filename_info_to_df(df, "Filename")

    # Load triple count data
    triple_path = f_dir / "triple_count_comparison.csv"
    triple_df = pd.read_csv(triple_path)
    triple_df = clean_db_sizes(triple_df)
    triple_df = add_filename_info_to_df(triple_df, "Filename")
    triple_df["triple_diff"] = triple_df["numberOfTriples_After"] - triple_df["numberOfTriples_Before"]

    # Custom order: "no_values" first, then alphabetical, with "every_type" at the end
    unique_types = df["val_type"].unique()
    ordered_types = []

    # Add "no_values" first if it exists
    if "no_values" in unique_types:
        ordered_types.append("no_values")

    # Add other types alphabetically (excluding "no_values" and "every_type")
    other_types = sorted([t for t in unique_types if t not in ["no_values", "every_type"]])
    ordered_types.extend(other_types)

    # Add "every_type" at the end if it exists
    if "every_type" in unique_types:
        ordered_types.append("every_type")

    # Calculate average excluding "no_values" and "every_type"
    filtered_df = df[~df["val_type"].isin(["no_values", "every_type"])]
    avg_db_after = filtered_df["DB_After"].mean()

    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=df, x="val_type", y="DB_After", estimator="mean", errorbar=("ci", 95), order=ordered_types)
    plt.axhline(y=avg_db_after, color="red", linestyle="--", label=f"Average: {avg_db_after:.2f} GB")

    # Add triple difference numbers on top of bars
    for i, val_type in enumerate(ordered_types):
        # Calculate mean triple difference for this value type
        type_triple_data = triple_df[triple_df["val_type"] == val_type]
        if len(type_triple_data) > 0:
            mean_triple_diff = type_triple_data["triple_diff"].mean()
            # Get the height of the bar
            bar_height = df[df["val_type"] == val_type]["DB_After"].mean()
            # Add text on top of the bar
            ax.text(
                i,
                bar_height + 0.1,
                f"{int(mean_triple_diff):,}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

    plt.ylim(0, df["DB_After"].max() * 1.2)  # Increased margin for text
    plt.xlabel("Value Type")
    plt.ylabel("DB Size After (GB)")
    plt.title("Database Size by Value Type")
    plt.legend()
    plt.xticks(rotation=45)

    # Add note about triple differences
    plt.figtext(
        0.02, 0.02, "Numbers on bars: Triple count difference (After - Before)", fontsize=8, style="italic", alpha=0.7
    )
    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/db_size_value_comparison_plot.png")
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
    # Filter to keep only data where res_num stays constant (isolate val_num effect)
    for i, val_type in enumerate(unique_types):
        type_data = df[df["val_type"] == val_type]
        # For each val_type, find the most common res_num and filter to that
        most_common_res = (
            type_data["res_num"].mode()[0] if len(type_data["res_num"].mode()) > 0 else type_data["res_num"].iloc[0]
        )
        filtered_data = type_data[type_data["res_num"] == most_common_res].sort_values("val_num")
        ax1.plot(
            filtered_data["val_num"],
            filtered_data["DB_After"],
            marker="o",
            color=colors[i],
            label=val_type,
            linewidth=2,
            alpha=0.7,
        )

    ax1.set_xlabel("Number of Values")
    ax1.set_ylabel("DB Size After (GB)")
    ax1.set_title("Database Size vs Number of Values")
    ax1.grid(True, alpha=0.3)
    ax1.legend(title="Value Type")

    # Plot 2: DB Size vs Number of Resources (one line per val_type)
    # Filter to keep only data where val_num stays constant (isolate res_num effect)
    for i, val_type in enumerate(unique_types):
        type_data = df[df["val_type"] == val_type]
        # For each val_type, find the most common val_num and filter to that
        most_common_val = (
            type_data["val_num"].mode()[0] if len(type_data["val_num"].mode()) > 0 else type_data["val_num"].iloc[0]
        )
        filtered_data = type_data[type_data["val_num"] == most_common_val].sort_values("res_num")
        ax2.plot(
            filtered_data["res_num"],
            filtered_data["DB_After"],
            marker="o",
            color=colors[i],
            label=val_type,
            linewidth=2,
            alpha=0.7,
        )

    ax2.set_xlabel("Number of Resources")
    ax2.set_ylabel("DB Size After (GB)")
    ax2.set_title("Database Size vs Number of Resources")
    ax2.grid(True, alpha=0.3)
    ax2.legend(title="Value Type")

    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/val_res_num_increasing_plot.png")
    plt.close()

    # Save individual plots separately
    # Plot 1: Number of Values
    plt.figure(figsize=(12, 6))
    growth_rates_values = []

    for i, val_type in enumerate(unique_types):
        type_data = df[df["val_type"] == val_type]
        most_common_res = (
            type_data["res_num"].mode()[0] if len(type_data["res_num"].mode()) > 0 else type_data["res_num"].iloc[0]
        )
        filtered_data = type_data[type_data["res_num"] == most_common_res].sort_values("val_num")

        # Calculate growth rate
        if len(filtered_data) > 1:
            val_range = filtered_data["val_num"].max() - filtered_data["val_num"].min()
            db_range = filtered_data["DB_After"].max() - filtered_data["DB_After"].min()
            growth_per_value = db_range / val_range if val_range > 0 else 0
        else:
            growth_per_value = 0

        growth_rates_values.append((val_type, growth_per_value))

        plt.plot(
            filtered_data["val_num"],
            filtered_data["DB_After"],
            marker="o",
            color=colors[i],
            label=val_type,
            linewidth=2,
            alpha=0.7,
        )

    plt.xlabel("Number of Values")
    plt.ylabel("DB Size After (GB)")
    plt.title("Database Size vs Number of Values")
    plt.grid(True, alpha=0.3)
    plt.legend(title="Value Type")

    # Add growth rates text
    text_str = "Growth Rates (GB per value):\n"
    for val_type, rate in growth_rates_values:
        text_str += f"{val_type}: {rate:.4f}\n"
    plt.text(
        1.02,
        0.5,
        text_str,
        transform=plt.gca().transAxes,
        fontsize=9,
        verticalalignment="center",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/db_size_vs_values.png", bbox_inches="tight")
    plt.close()

    # Plot 2: Number of Resources
    plt.figure(figsize=(12, 6))
    growth_rates_resources = []

    for i, val_type in enumerate(unique_types):
        type_data = df[df["val_type"] == val_type]
        most_common_val = (
            type_data["val_num"].mode()[0] if len(type_data["val_num"].mode()) > 0 else type_data["val_num"].iloc[0]
        )
        filtered_data = type_data[type_data["val_num"] == most_common_val].sort_values("res_num")

        # Calculate multiplication factor
        if len(filtered_data) > 1:
            min_db = filtered_data["DB_After"].min()
            max_db = filtered_data["DB_After"].max()
            multiplication_factor = max_db / min_db if min_db > 0 else 0
        else:
            multiplication_factor = 0

        growth_rates_resources.append((val_type, multiplication_factor))

        plt.plot(
            filtered_data["res_num"],
            filtered_data["DB_After"],
            marker="o",
            color=colors[i],
            label=val_type,
            linewidth=2,
            alpha=0.7,
        )

    plt.xlabel("Number of Resources")
    plt.ylabel("DB Size After (GB)")
    plt.title("Database Size vs Number of Resources")
    plt.grid(True, alpha=0.3)
    plt.legend(title="Value Type")

    # Add multiplication factors text
    text_str = "Multiplication Factors:\n"
    for val_type, factor in growth_rates_resources:
        text_str += f"{val_type}: {factor:.2f}x\n"
    plt.text(
        1.02,
        0.5,
        text_str,
        transform=plt.gca().transAxes,
        fontsize=9,
        verticalalignment="center",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    plt.tight_layout()
    plt.savefig("x_fuseki_bloating_files/graphics_output/db_size_vs_resources.png", bbox_inches="tight")
    plt.close()


prepare_fuseki_multiple_uploads()
prepare_val_res_num_increasing()
prepare_fuseki_size_value_comparison()
