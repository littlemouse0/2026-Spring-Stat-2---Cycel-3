"""
Question 1 Analysis: Gender and Current Cigarette Use

This script reads a cleaned CSV file, calculates descriptive statistics,
performs a two-proportion z-test and chi-square test, saves results, and
creates a bar plot.

Default input:
    data/processed/q1_gender_cigarette_cleaned.csv

Run example:
    python c3_data_analysis.py

Or specify paths:
    python c3_data_analysis.py --input data/processed/q1_gender_cigarette_cleaned.csv --output outputs
"""

from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")


REQUIRED_COLUMNS = ["Gender", "Current_Cigarette_Binary"]
GENDER_ORDER = ["Female", "Male"]
BINARY_ORDER = [0, 1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze gender differences in current cigarette use."
    )
    parser.add_argument(
        "--input",
        default="data/processed/q1_gender_cigarette_cleaned.csv",
        help="Path to the cleaned input CSV file.",
    )
    parser.add_argument(
        "--output",
        default="outputs",
        help="Output folder for tables, summary, and figures.",
    )
    return parser.parse_args()


def create_output_folders(output_dir: Path) -> dict[str, Path]:
    folders = {
        "figures": output_dir / "figures",
        "tables": output_dir / "tables",
        "summary": output_dir / "summary",
    }

    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)

    return folders


def read_cleaned_data(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}\n"
            "Please check your file path or use --input to specify the CSV file."
        )

    df = pd.read_csv(input_path)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns) + "\n"
            f"Available columns: {list(df.columns)}"
        )

    df = df.dropna(subset=REQUIRED_COLUMNS).copy()

    # Keep only Female and Male because the hypothesis test compares these two groups.
    df = df[df["Gender"].isin(GENDER_ORDER)].copy()

    # Convert the response variable to numeric 0/1 if possible.
    df["Current_Cigarette_Binary"] = pd.to_numeric(
        df["Current_Cigarette_Binary"], errors="coerce"
    )
    df = df.dropna(subset=["Current_Cigarette_Binary"])
    df["Current_Cigarette_Binary"] = df["Current_Cigarette_Binary"].astype(int)
    df = df[df["Current_Cigarette_Binary"].isin(BINARY_ORDER)].copy()

    if df.empty:
        raise ValueError(
            "No valid rows remain after filtering for Gender = Female/Male and "
            "Current_Cigarette_Binary = 0/1."
        )

    return df


def build_count_table(df: pd.DataFrame) -> pd.DataFrame:
    count_table = pd.crosstab(df["Gender"], df["Current_Cigarette_Binary"])

    # Reindex to avoid errors when one group or response category is absent.
    count_table = count_table.reindex(index=GENDER_ORDER, columns=BINARY_ORDER, fill_value=0)

    count_table.columns = ["No_Current_Cigarette_Use", "Current_Cigarette_Use"]
    count_table["Total"] = count_table.sum(axis=1)

    if (count_table["Total"] == 0).any():
        missing_groups = count_table.index[count_table["Total"] == 0].tolist()
        raise ValueError(
            "The following gender group(s) have zero observations: "
            + ", ".join(missing_groups)
        )

    count_table["Current_Cigarette_Proportion"] = (
        count_table["Current_Cigarette_Use"] / count_table["Total"]
    )

    return count_table


def run_two_proportion_z_test(count_table: pd.DataFrame) -> dict[str, float]:
    female_current = count_table.loc["Female", "Current_Cigarette_Use"]
    female_total = count_table.loc["Female", "Total"]
    male_current = count_table.loc["Male", "Current_Cigarette_Use"]
    male_total = count_table.loc["Male", "Total"]

    p_female = female_current / female_total
    p_male = male_current / male_total
    diff = p_female - p_male

    p_pool = (female_current + male_current) / (female_total + male_total)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / female_total + 1 / male_total))

    if se_pool == 0:
        raise ValueError("The pooled standard error is zero, so the z-test cannot be computed.")

    z_stat = diff / se_pool
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    se_unpooled = np.sqrt(
        (p_female * (1 - p_female) / female_total)
        + (p_male * (1 - p_male) / male_total)
    )
    ci_lower = diff - 1.96 * se_unpooled
    ci_upper = diff + 1.96 * se_unpooled

    return {
        "female_current": float(female_current),
        "female_total": float(female_total),
        "male_current": float(male_current),
        "male_total": float(male_total),
        "p_female": float(p_female),
        "p_male": float(p_male),
        "diff": float(diff),
        "z_stat": float(z_stat),
        "p_value": float(p_value),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
    }


def run_chi_square_test(df: pd.DataFrame) -> dict[str, float]:
    chi2_table = pd.crosstab(df["Gender"], df["Current_Cigarette_Binary"])
    chi2_table = chi2_table.reindex(index=GENDER_ORDER, columns=BINARY_ORDER, fill_value=0)

    chi2_stat, chi2_p_value, dof, expected = stats.chi2_contingency(chi2_table)

    return {
        "chi2_stat": float(chi2_stat),
        "chi2_p_value": float(chi2_p_value),
        "dof": int(dof),
    }


def make_conclusion(p_value: float, alpha: float = 0.05) -> str:
    if p_value < alpha:
        return (
            "Reject the null hypothesis. There is statistically significant evidence "
            "that the proportion of current cigarette use differs between male and "
            "female students."
        )

    return (
        "Fail to reject the null hypothesis. There is not enough statistically "
        "significant evidence to conclude that the proportion of current cigarette "
        "use differs between male and female students."
    )


def save_test_results(
    table_dir: Path,
    z_results: dict[str, float],
    chi_square_results: dict[str, float],
) -> Path:
    test_results = pd.DataFrame(
        {
            "Test": ["Two-proportion z-test", "Chi-square test of independence"],
            "Statistic": [z_results["z_stat"], chi_square_results["chi2_stat"]],
            "P_value": [z_results["p_value"], chi_square_results["chi2_p_value"]],
        }
    )

    output_path = table_dir / "q1_gender_cigarette_test_results.csv"
    test_results.to_csv(output_path, index=False)
    return output_path


def save_summary(
    summary_dir: Path,
    count_table: pd.DataFrame,
    z_results: dict[str, float],
    chi_square_results: dict[str, float],
    conclusion: str,
) -> Path:
    summary_path = summary_dir / "q1_gender_cigarette_analysis_summary.txt"

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Question 1: Gender and Current Cigarette Use\n")
        f.write("=" * 60 + "\n\n")

        f.write("Research question:\n")
        f.write(
            "Is the proportion of current cigarette use different between male "
            "and female students?\n\n"
        )

        f.write("Variables:\n")
        f.write("- Group variable: Gender, based on WhatIsYourSex\n")
        f.write(
            "- Response variable: Current_Cigarette_Binary, based on "
            "CurrentCigaretteUse\n"
        )
        f.write(
            "- Current_Cigarette_Binary: 1 = current cigarette use, "
            "0 = no current cigarette use\n\n"
        )

        f.write("Hypotheses:\n")
        f.write(
            "H0: The proportion of current cigarette use is the same for male "
            "and female students.\n"
        )
        f.write(
            "HA: The proportion of current cigarette use is different between "
            "male and female students.\n\n"
        )

        f.write("Descriptive statistics:\n")
        f.write(str(count_table))
        f.write("\n\n")

        f.write("Two-proportion z-test results:\n")
        f.write(f"Female proportion: {z_results['p_female']:.4f}\n")
        f.write(f"Male proportion: {z_results['p_male']:.4f}\n")
        f.write(f"Difference, Female - Male: {z_results['diff']:.4f}\n")
        f.write(f"Z statistic: {z_results['z_stat']:.4f}\n")
        f.write(f"P-value: {z_results['p_value']:.4f}\n")
        f.write(
            "95% CI for difference: "
            f"({z_results['ci_lower']:.4f}, {z_results['ci_upper']:.4f})\n\n"
        )

        f.write("Chi-square test results:\n")
        f.write(f"Chi-square statistic: {chi_square_results['chi2_stat']:.4f}\n")
        f.write(f"Degrees of freedom: {chi_square_results['dof']}\n")
        f.write(f"P-value: {chi_square_results['chi2_p_value']:.4f}\n\n")

        f.write("Conclusion:\n")
        f.write(conclusion)

    return summary_path


def create_bar_plot(figure_dir: Path, count_table: pd.DataFrame) -> Path:
    plot_data = count_table[["Current_Cigarette_Proportion"]].copy()
    output_path = figure_dir / "q1_gender_cigarette_barplot.png"

    plt.figure(figsize=(6, 4))
    plt.bar(plot_data.index, plot_data["Current_Cigarette_Proportion"])
    plt.xlabel("Gender")
    plt.ylabel("Proportion of Current Cigarette Use")
    plt.title("Current Cigarette Use by Gender")

    y_max = plot_data["Current_Cigarette_Proportion"].max()
    plt.ylim(0, min(1, y_max + 0.05) if y_max > 0.95 else y_max + 0.05)

    for i, value in enumerate(plot_data["Current_Cigarette_Proportion"]):
        plt.text(i, value + 0.01, f"{value:.3f}", ha="center")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    return output_path


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_folders = create_output_folders(output_dir)

    df = read_cleaned_data(input_path)

    print("--- Data Preview ---")
    print(df.head())

    print("\n--- Variables in cleaned data ---")
    print(df.columns.tolist())

    count_table = build_count_table(df)
    count_table_path = output_folders["tables"] / "q1_gender_cigarette_count_table.csv"
    count_table.to_csv(count_table_path)

    print("\n--- Frequency and proportion table ---")
    print(count_table)

    z_results = run_two_proportion_z_test(count_table)
    chi_square_results = run_chi_square_test(df)
    test_results_path = save_test_results(
        output_folders["tables"], z_results, chi_square_results
    )
    conclusion = make_conclusion(z_results["p_value"])
    summary_path = save_summary(
        output_folders["summary"],
        count_table,
        z_results,
        chi_square_results,
        conclusion,
    )
    figure_path = create_bar_plot(output_folders["figures"], count_table)

    print("\n--- Two-proportion z-test results ---")
    print(f"Female current cigarette use proportion: {z_results['p_female']:.4f}")
    print(f"Male current cigarette use proportion: {z_results['p_male']:.4f}")
    print(f"Difference in proportions, Female - Male: {z_results['diff']:.4f}")
    print(f"Z statistic: {z_results['z_stat']:.4f}")
    print(f"P-value: {z_results['p_value']:.4f}")
    print(
        "95% CI for difference: "
        f"({z_results['ci_lower']:.4f}, {z_results['ci_upper']:.4f})"
    )

    print("\n--- Chi-square test results ---")
    print(f"Chi-square statistic: {chi_square_results['chi2_stat']:.4f}")
    print(f"Degrees of freedom: {chi_square_results['dof']}")
    print(f"P-value: {chi_square_results['chi2_p_value']:.4f}")

    print("\n--- Conclusion ---")
    print(conclusion)

    print("\nAnalysis completed.")
    print("Outputs saved:")
    print(f"1. {count_table_path}")
    print(f"2. {test_results_path}")
    print(f"3. {summary_path}")
    print(f"4. {figure_path}")


if __name__ == "__main__":
    main()
