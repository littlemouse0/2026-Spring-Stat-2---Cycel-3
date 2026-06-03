# 2026-Sprint-Stat-2-Cycle-3

## Group Information

- Group number: 6
- Members: 111370210李采軒、112370144林謙宏

## Dataset

- Original dataset: `YRBS_2007.csv`
- Cleaned dataset: `q1_gender_cigarette_cleaned.csv`

## Selected Research Question

This project selects **Question 1: Gender and Current Cigarette Use**.

Research question:

- Is the proportion of current cigarette use different between male and female students?

中文：

- 男性與女性學生目前吸菸的比例是否不同？

## Variables

- Group variable: `WhatIsYourSex`
- Response variable: `CurrentCigaretteUse`
- Cleaned group variable: `Gender`
- Cleaned response variable: `Current_Cigarette_Binary`

## Group Definition

This project compares two independent groups:

- Female students
- Male students

## Response Variable

The response variable is current cigarette use.

Because current cigarette use is a binary categorical variable, this project compares the proportion of current cigarette use between female and male students.

The cleaned response variable was coded as:

- `1 = Current cigarette use`
- `0 = No current cigarette use`

## Recoding Rules

The original variables were recoded as follows:

### Gender

- `WhatIsYourSex = 1` → `Female`
- `WhatIsYourSex = 2` → `Male`

### Current Cigarette Use

- `CurrentCigaretteUse = 1` → `0`, no current cigarette use
- `CurrentCigaretteUse = 2–7` → `1`, current cigarette use

Rows with missing or invalid values were removed before the final analysis.

## Statistical Method

The statistical method used in this project is:

- Two-proportion z-test

The two-proportion z-test was used because this project compares the proportion of current cigarette use between two independent groups.

The significance level was:

- `α = 0.05`

A chi-square test of independence was also included as an additional check.

## Project Workflow

This project was completed in the following steps:

1. Selected the research question
2. Defined the two groups
3. Defined the response variable
4. Cleaned the original dataset
5. Recoded gender and current cigarette use
6. Created the cleaned dataset
7. Created frequency and proportion tables
8. Completed descriptive statistics
9. Completed two-proportion z-test
10. Created visualizations
11. Prepared a one-page infographic summary

## Files

### Python Script Files

- `資料處理(1).py`
- `資料分析(1).py`

### Data Files

- `YRBS_2007(3).csv`
- `q1_gender_cigarette_cleaned(1).csv`

### Table Output Files

- `q1_frequency_table(1).csv`
- `q1_proportion_table(1).csv`
- `q1_gender_cigarette_count_table(1).csv`
- `q1_gender_cigarette_test_results(1).csv`

### Summary Output Files

- `q1_data_processing_summary(1).txt`
- `q1_gender_cigarette_analysis_summary(1).txt`

### Figure Output Files

- `q1_current_cigarette_use_by_gender_barplot.png`
- `q1_difference_in_proportions_95ci.png`

### Infographic Summary

- `cycle3_infographic_summary.pptx`
- `cycle_3_infographic_summary_cigarette_use_by_gend.png`

## Descriptive Results

After data cleaning, the final sample size was:

- `n = 13,312`

The group summaries were:

| Gender | No Current Cigarette Use | Current Cigarette Use | Total | Current Cigarette Use Proportion |
|---|---:|---:|---:|---:|
| Female | 5,573 | 1,167 | 6,740 | 0.1731 |
| Male | 5,154 | 1,418 | 6,572 | 0.2158 |

The descriptive statistics showed that male students had a higher current cigarette use proportion than female students.

## Main Result

The two-proportion z-test was used to test whether the current cigarette use proportion was different between male and female students.

The result was:

| Result | Value |
|---|---:|
| Female proportion | 0.1731 |
| Male proportion | 0.2158 |
| Difference, Female - Male | -0.0426 |
| z statistic | -6.2148 |
| p-value | < 0.001 |
| 95% confidence interval | (-0.0561, -0.0292) |

At the significance level `α = 0.05`, the p-value was less than 0.05. Therefore, the null hypothesis was rejected.

## Conclusion

Based on the analysis, the proportion of current cigarette use was significantly different between male and female students in the YRBS 2007 dataset.

Male students had a higher current cigarette use proportion than female students.

The estimated difference was about 4.26 percentage points, with males higher than females.

Because this project uses observational survey data, the result should be interpreted as an association, not as a causal relationship.

## Video Link

The project video can be added here:

- [VIDEO LINK](請貼上影片連結)
