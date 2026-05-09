from pathlib import Path
import warnings

import pandas as pd

warnings.filterwarnings("ignore")


def find_project_root(start_path=None):
    """
    從目前位置往上找 project-cycle-3 專案根目錄。
    只要找到同時包含 data、notebooks、outputs 的資料夾，就視為專案根目錄。
    """
    if start_path is None:
        start_path = Path.cwd()

    start_path = Path(start_path).resolve()

    for path in [start_path, *start_path.parents]:
        if (
            (path / "data").exists()
            and (path / "notebooks").exists()
            and (path / "outputs").exists()
        ):
            return path

    raise FileNotFoundError(
        "找不到專案根目錄。請確認你的資料夾結構是 project-cycle-3/data、notebooks、outputs。"
    )


def main():
    # --------------------------------------------------
    # 1. Project folder structure
    # --------------------------------------------------
    project_root = find_project_root()

    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"

    output_dir = project_root / "outputs"
    figure_dir = output_dir / "figures"
    table_dir = output_dir / "tables"
    summary_dir = output_dir / "summary"

    report_dir = project_root / "report"
    references_dir = project_root / "references"

    folders = [
        raw_dir,
        processed_dir,
        figure_dir,
        table_dir,
        summary_dir,
        report_dir,
        references_dir,
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # 2. File paths
    # --------------------------------------------------
    data_file_name = "YRBS_2007.csv"

    input_path = raw_dir / data_file_name
    cleaned_output_path = processed_dir / "q1_gender_cigarette_cleaned.csv"
    frequency_table_path = table_dir / "q1_frequency_table.csv"
    proportion_table_path = table_dir / "q1_proportion_table.csv"
    summary_path = summary_dir / "q1_data_processing_summary.txt"

    if not input_path.exists():
        raise FileNotFoundError(
            f"找不到資料檔案：{input_path}\n"
            "請把 YRBS_2007.csv 放到 project-cycle-3/data/raw/ 裡面。"
        )

    print("Project root:", project_root)
    print("Input file:", input_path)

    # --------------------------------------------------
    # 3. Read data
    # --------------------------------------------------
    df_raw = pd.read_csv(input_path)
    df_raw.columns = df_raw.columns.str.strip()

    # Question 1 variables
    group_var = "WhatIsYourSex"
    response_var = "CurrentCigaretteUse"
    required_columns = [group_var, response_var]

    missing_columns = [col for col in required_columns if col not in df_raw.columns]

    if missing_columns:
        raise KeyError(
            f"CSV 缺少必要欄位：{missing_columns}\n"
            f"目前 CSV 欄位有：{list(df_raw.columns)}"
        )

    df = df_raw[required_columns].copy()

    print("\n--- Missing values before cleaning ---")
    print(df.isnull().sum())

    # --------------------------------------------------
    # 4. Recode variables
    # --------------------------------------------------
    # WhatIsYourSex:
    # 1 = Female
    # 2 = Male
    df["Gender"] = df[group_var].map(
        {
            1.0: "Female",
            2.0: "Male",
        }
    )

    # CurrentCigaretteUse:
    # 1 = 0 days, coded as 0
    # 2-7 = at least 1 day, coded as 1
    df["Current_Cigarette_Binary"] = df[response_var].map(
        {
            1.0: 0,
            2.0: 1,
            3.0: 1,
            4.0: 1,
            5.0: 1,
            6.0: 1,
            7.0: 1,
        }
    )

    # --------------------------------------------------
    # 5. Remove missing / invalid values
    # --------------------------------------------------
    df_clean = df.dropna(subset=["Gender", "Current_Cigarette_Binary"]).copy()
    df_clean["Current_Cigarette_Binary"] = df_clean["Current_Cigarette_Binary"].astype(int)

    # --------------------------------------------------
    # 6. Save cleaned data
    # --------------------------------------------------
    df_clean.to_csv(cleaned_output_path, index=False, encoding="utf-8-sig")

    # --------------------------------------------------
    # 7. Create summary tables
    # --------------------------------------------------
    frequency_table = pd.crosstab(
        df_clean["Gender"],
        df_clean["Current_Cigarette_Binary"],
        margins=True,
    )

    proportion_table = pd.crosstab(
        df_clean["Gender"],
        df_clean["Current_Cigarette_Binary"],
        normalize="index",
    )

    frequency_table.to_csv(frequency_table_path, encoding="utf-8-sig")
    proportion_table.to_csv(proportion_table_path, encoding="utf-8-sig")

    # --------------------------------------------------
    # 8. Print results
    # --------------------------------------------------
    print("\n" + "-" * 60)
    print("Variable definition and coding completed")
    print(f"Final sample size after cleaning: n = {len(df_clean)}")
    print("-" * 60)

    print("\n--- Cleaned data preview ---")
    print(df_clean[[group_var, response_var, "Gender", "Current_Cigarette_Binary"]].head())

    print("\n--- Frequency table ---")
    print(frequency_table)

    print("\n--- Proportion table ---")
    print(proportion_table)

    print("\n--- Output files ---")
    print("Cleaned data:", cleaned_output_path)
    print("Frequency table:", frequency_table_path)
    print("Proportion table:", proportion_table_path)
    print("Summary:", summary_path)

    # --------------------------------------------------
    # 9. Save summary text
    # --------------------------------------------------
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Question 1: Gender and Current Cigarette Use\n")
        f.write("=" * 50 + "\n\n")

        f.write("Research question:\n")
        f.write(
            "Is the proportion of current cigarette use different between "
            "male and female students?\n\n"
        )

        f.write("Project paths:\n")
        f.write(f"- Project root: {project_root}\n")
        f.write(f"- Raw data: {input_path}\n")
        f.write(f"- Processed data: {cleaned_output_path}\n")
        f.write(f"- Frequency table: {frequency_table_path}\n")
        f.write(f"- Proportion table: {proportion_table_path}\n\n")

        f.write("Variables:\n")
        f.write(f"- Group variable: {group_var}\n")
        f.write(f"- Response variable: {response_var}\n\n")

        f.write("Coding:\n")
        f.write("- Gender: 1 = Female, 2 = Male\n")
        f.write(
            "- Current_Cigarette_Binary: "
            "0 = No current cigarette use, "
            "1 = Current cigarette use\n\n"
        )

        f.write("Missing values before cleaning:\n")
        f.write(str(df.isnull().sum()))
        f.write("\n\n")

        f.write(f"Final sample size after cleaning: n = {len(df_clean)}\n\n")

        f.write("Frequency table:\n")
        f.write(str(frequency_table))
        f.write("\n\n")

        f.write("Proportion table:\n")
        f.write(str(proportion_table))
        f.write("\n")

    print("\nProcessing finished successfully.")


if __name__ == "__main__":
    main()