# Technical Workflow

This document describes how the project moves from Pew Research Center American Trends Panel Wave 144 public-use microdata to the final tab book. For the authoritative explanation of analytical universes, weighting, effective bases, significance testing, and limitations, see the [methodology](methodology.md).

## Workflow Overview

```text
Questionnaire / Public-Use Data
        ↓
Raw Survey Data
        ↓
Data Validation
        ↓
Variable Selection
        ↓
Tabulation Plan
        ↓
Weighted Cross-Tabs
        ↓
Effective Sample Sizes
        ↓
Significance Testing
        ↓
Final QA & Small-Base Screening
        ↓
Excel Tab Book
```

The workflow is implemented through six sequential Python scripts.

## 1. Data Validation

`scripts/python/01_data_validation.py`

The first stage validates the source dataset before analysis. Checks cover expected dataset dimensions, required analytical and platform-use variables, routing consistency, derived Facebook/Instagram routing, demographic-banner availability, and survey-weight availability. Platform routing and derived-universe checks must pass before the pipeline proceeds.

## 2. Variable Selection

`scripts/python/02_variable_selection.py`

The second stage defines and validates the analytical scope:

- 28 platform-specific WHY variables
- five primary demographic banners: Age, Gender, Education, Census Region, and Income
- platform-specific survey weights
- platform-specific analytical universes

All 28 WHY variables are validated against their platform-specific universes. The stage reports missing responses inside each universe, rejects responses outside their routed universe, and fails on nonnumeric, nonfinite, nonpositive, or missing analytical weights. Detailed or secondary demographic variables are excluded from the primary tab book to keep the output focused and interpretable.

The documented decisions are available in the [variable-selection matrix](../tabulation/variable_selection_matrix.csv) and [tabulation plan](../tabulation/tabulation_plan.csv).

## 3. Weighted Cross-Tabulation

`scripts/python/03_tabulation_engine.py`

The tabulation engine generates all 28 analytical tables from the raw W144 data and saved tabulation plan. Each table contains Total plus Age, Gender, Education, Census Region, and Income banners, producing 18 analytical columns. Every column displays an unweighted base and weighted percentages for Major reason, Minor reason, and Not a reason.

Weighted percentages use the appropriate platform-specific survey weight. Special response code `99` is excluded from the substantive percentage denominator. The script performs 504 percentage-sum QA checks and exports `output/tables/T01.csv` through `output/tables/T28.csv`.

## 4. Effective Sample Size and Significance Testing

`scripts/python/04_significance_testing.py`

The fourth stage calculates Kish-adjusted effective sample sizes and performs pairwise column-proportion tests within each demographic banner:

```text
n_eff = (sum(w))² / sum(w²)
```

Pairwise tests use weighted percentage estimates, Kish-adjusted effective sample sizes, two-sided tests, a 95% confidence level, and a minimum unweighted test base of N = 100. The pipeline generates 504 effective-base records and 1,596 pairwise tests, of which 495 are significant under the project procedure. No category with an unweighted base below 100 enters testing.

Outputs:

- `qa/effective_bases.csv`
- `qa/significance_test_results.csv`

No multiplicity adjustment is applied; significance results are exploratory. See the [methodology](methodology.md) for the complete statistical interpretation and limitations.

## 5. Final QA and Small-Base Screening

`scripts/python/05_final_qa.py`

The final QA stage independently rebuilds key analytical outputs and reconciles them with upstream results. It checks:

- 28 of 28 table-level percentage validations
- 504 persisted unweighted bases
- 1,512 persisted weighted percentages
- 504 effective-base records
- significance-result structure and pairwise-test uniqueness
- low-base exclusions from significance testing
- platform and table coverage
- small-base classifications

A total of 476 demographic banner cells are screened:

| Base classification | Cells |
|---|---:|
| N ≥ 100 | 448 |
| 30 ≤ N < 100 | 21 |
| N < 30 | 7 |

All 28 cells below N = 100 belong to the `Gender | In some other way` category. Display notation is `*` for N = 30–99 and `**` for N below 30.

Outputs:

- `qa/qa_summary.csv`
- `qa/small_base_qa.csv`

## 6. Automated Excel Tab Book

`scripts/python/06_excel_export.py`

The final stage generates `output/tab_books/Reach3_Social_Media_TabBook.xlsx` from the 28 table CSVs, tabulation plan, significance-test results, small-base QA, and final table-level QA.

The workbook contains eight sheets:

1. `01_README`
2. `02_CONTENTS`
3. `03_METHODOLOGY`
4. `04_FACEBOOK`
5. `05_INSTAGRAM`
6. `06_X`
7. `07_TIKTOK`
8. `08_QA_SUMMARY`

The four platform sheets contain seven stacked tables each. The export includes grouped banner headers, comparison letters, unweighted bases, weighted percentages, significance markers, small-base flags, methodological footnotes, and QA documentation.

After saving, the stage reopens the actual workbook and verifies all 28 table placements, 504 displayed bases, 1,512 displayed percentages, small-base notation, and stored significance letters. It confirms that 342 analytical cells receive one or more significance letters.

## Significance-Letter Interpretation

Within each demographic banner, categories are assigned letters such as A, B, C, and D. A letter appended to a percentage indicates that the percentage is statistically higher than the category represented by that letter at the 95% confidence level under the project procedure. For example, `10.4% CD` indicates that the displayed percentage is significantly higher than categories C and D. Categories with unweighted bases below 100 are excluded from testing.

## Quality Assurance

QA is built into every stage. The workflow validates questionnaire routing, analytical universes, required variables, response codes, survey weights, table structure, percentage sums, effective sample sizes, test uniqueness and coverage, low-base exclusions, small-base classifications, exported CSV structure, persisted base and percentage values, workbook structure, displayed values, and significance markers.

Validated final results:

```text
28 / 28 tables passing percentage QA
504 / 504 analytical percentage checks passing
1,596 pairwise tests validated
495 significant pairwise comparisons
342 analytical cells receiving significance markers
0 low-base categories entering significance testing
```

## Repository Structure

```text
Social-Media-Survey-Tabulation/
├── README.md
├── requirements.txt
├── documentation/
│   ├── methodology.md
│   └── workflow.md
├── scripts/python/
│   ├── 01_data_validation.py
│   ├── 02_variable_selection.py
│   ├── 03_tabulation_engine.py
│   ├── 04_significance_testing.py
│   ├── 05_final_qa.py
│   └── 06_excel_export.py
├── tabulation/
│   ├── tabulation_plan.csv
│   └── variable_selection_matrix.csv
├── output/
│   ├── tables/T01.csv ... T28.csv
│   └── tab_books/Reach3_Social_Media_TabBook.xlsx
└── qa/
    ├── effective_bases.csv
    ├── significance_test_results.csv
    ├── qa_summary.csv
    └── small_base_qa.csv
```

Raw survey data and original source documentation are maintained locally and excluded from version control.

## Reproduction

The project was developed and validated using Python 3.11. Install dependencies:

```bash
py -3.11 -m pip install -r requirements.txt
```

Obtain the public-use W144 dataset from the [official Pew Research Center source](https://www.pewresearch.org/dataset/american-trends-panel-wave-144/) and place the CSV at:

```text
data/raw/ATP_W144.csv
```

Run the pipeline sequentially:

```bash
py -3.11 scripts/python/01_data_validation.py
py -3.11 scripts/python/02_variable_selection.py
py -3.11 scripts/python/03_tabulation_engine.py
py -3.11 scripts/python/04_significance_testing.py
py -3.11 scripts/python/05_final_qa.py
py -3.11 scripts/python/06_excel_export.py
```

A successful run regenerates the analytical tables, QA outputs, significance-test results, and final Excel tab book.

## Statistical Limitations

The significance tests use weighted estimates and Kish-adjusted effective sample sizes. They demonstrate a reproducible survey-tabulation and QA workflow; they do not reproduce Pew Research Center's complete complex-survey variance-estimation procedure. No multiplicity adjustment is applied, so significance markers should be interpreted as exploratory.

## Portfolio Context

The project demonstrates questionnaire and routing interpretation, survey-data validation, tabulation planning, weighted cross-tabulation, demographic banner construction, effective-base calculation, significance testing, small-base handling, discrepancy investigation, automated QA, Excel tab-book production, and reproducible analytical documentation.
