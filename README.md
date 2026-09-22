# Social Media Platform Usage & User Motivations

### Survey Tabulation, Statistical Testing & QA Workflow

This project demonstrates an end-to-end survey tabulation workflow using public-use data from the Pew Research Center American Trends Panel Wave 144 (W144), conducted March 18–24, 2024.

The project was designed as a market-research and survey-processing portfolio study, with emphasis on reproducible cross-tabulation, weighting, significance testing, quality assurance, discrepancy investigation, and production of a formatted Excel tab book.

---

## Data Source

The analysis uses the Pew Research Center American Trends Panel Wave 144 public-use dataset.

The analytical dataset contains:

- 10,454 respondent records
- 195 variables
- survey weights
- demographic variables
- social-media usage variables
- platform-specific user-motivation batteries

The raw microdata are not redistributed in this repository. Obtain the W144 public-use dataset from the official Pew Research Center source.

To reproduce the analysis, place the W144 CSV file at:

```text
data/raw/ATP_W144.csv
```

Original source documentation is maintained locally and excluded from the repository.

---

## Research Question

How do social-media usage motivations differ across Facebook, Instagram, X, and TikTok, and across demographic groups?

Seven motivations are analyzed for each platform:

1. Get news
2. Keep up with politics or political issues
3. Keep up with sports or pop culture
4. Entertainment
5. Keep up with friends and family
6. Connect with others who share your interests
7. Look at product reviews or recommendations

This produces 28 analytical cross-tabulations:

- T01–T07: Facebook
- T08–T14: Instagram
- T15–T21: X
- T22–T28: TikTok

---

## Project Highlights

| Metric | Result |
|---|---:|
| Respondent records | 10,454 |
| Raw variables | 195 |
| Social platforms | 4 |
| Motivation variables | 28 |
| Cross-tab tables | 28 |
| Analytical columns per table | 18 |
| Percentage QA checks | 504 |
| Banner cells screened for base size | 476 |
| Pairwise significance tests | 1,596 |
| Significant comparisons at 95% | 495 |
| Cells receiving significance markers | 342 |
| Low-base categories entering significance tests | 0 |

---

## Key Findings

- On Facebook, 74.8% selected keeping up with friends and family as a major reason for using the platform.
- On TikTok, 81.4% selected entertainment as a major reason.
- On X, entertainment led at 44.8%, while shared interests, sports/pop culture, news, and politics formed a descriptive cluster between 24.3% and 28.3%.
- On Instagram, entertainment was a major reason for 65.3% of users ages 18–29 versus 32.8% of users ages 65+; this within-platform difference was statistically significant.
- On Facebook, friends and family was a major reason for 80.2% of women versus 67.6% of men; this within-platform difference was statistically significant.

Platform-level percentages describe different platform-specific or routed respondent universes, so comparisons across platforms are descriptive. Significance testing applies to demographic comparisons within a platform.

---

## Analytical Workflow

The project follows a reproducible survey-processing pipeline:

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

The complete workflow is implemented through six sequential Python scripts.

---

## 1. Data Validation

`scripts/python/01_data_validation.py`

The first stage validates the source dataset before analysis.

Checks include:

- expected dataset dimensions
- required analytical variables
- platform usage variables
- routing consistency
- derived Facebook/Instagram routing
- demographic banner availability
- survey-weight availability

Platform routing and derived-universe checks must pass before the analytical pipeline proceeds.

---

## 2. Variable Selection

`scripts/python/02_variable_selection.py`

The second stage defines the analytical variables used in the project.

The final analysis includes:

- 28 platform-specific WHY variables
- 5 primary demographic banners
- platform-specific survey weights
- platform-specific analytical universes

This stage also validates all 28 WHY variables against their
platform-specific universes and checks the integrity of every survey
weight used by the tabulation plan. It reports missing responses inside
each universe, rejects responses outside their routed universe, and fails
on nonnumeric, nonfinite, nonpositive, or missing analytical weights.

The five demographic banners are:

- Age
- Gender
- Education
- Census Region
- Income

Detailed or secondary demographic variables are excluded from the primary tab book to keep the output focused and interpretable.

---

## 3. Weighted Cross-Tabulation

`scripts/python/03_tabulation_engine.py`

The tabulation engine generates all 28 analytical tables from the raw W144 data and the saved tabulation plan.

Each table contains:

- Total
- Age
- Gender
- Education
- Region
- Income

This produces 18 analytical columns per table.

For each column, the table displays:

- Unweighted Base
- Major reason
- Minor reason
- Not a reason

Weighted percentages are calculated using the appropriate platform-specific survey weight.

Special response code `99` is excluded from the substantive percentage denominator.

The script performs 504 percentage-sum QA checks and exports:

```text
output/tables/T01.csv
...
output/tables/T28.csv
```

---

## 4. Effective Sample Size & Significance Testing

`scripts/python/04_significance_testing.py`

The significance-testing stage calculates Kish-adjusted effective sample sizes and performs pairwise column-proportion tests within each demographic banner.

Kish effective sample size is calculated as:

```text
n_eff = (sum(w))² / sum(w²)
```

Pairwise tests use:

- weighted percentage estimates
- Kish-adjusted effective sample sizes
- two-sided tests
- 95% confidence level
- minimum unweighted test base of N = 100

The pipeline generates:

- 504 effective-base records
- 1,596 pairwise significance tests
- 495 statistically significant pairwise comparisons

No category with an unweighted base below 100 enters significance testing.

Outputs:

```text
qa/effective_bases.csv
qa/significance_test_results.csv
```

No multiplicity adjustment is applied; significance results are exploratory.

---

## 5. Final QA & Small-Base Screening

`scripts/python/05_final_qa.py`

The final QA stage independently rebuilds key analytical outputs and reconciles them with upstream pipeline results.

Checks include:

- 28/28 table-level percentage QA
- independent reconciliation of 504 persisted unweighted bases
- independent reconciliation of 1,512 persisted weighted percentages
- 504/504 effective-base records
- significance-result structure
- low-base significance exclusions
- platform and table coverage
- small-base classification

A total of 476 demographic banner cells are reviewed:

| Base classification | Cells |
|---|---:|
| N ≥ 100 | 448 |
| 30 ≤ N < 100 | 21 |
| N < 30 | 7 |

All 28 cells with N < 100 belong to the `Gender | In some other way` category.

Small-base notation:

- `*` = N between 30 and 99
- `**` = N below 30

Outputs:

```text
qa/qa_summary.csv
qa/small_base_qa.csv
```

---

## 6. Automated Excel Tab Book

`scripts/python/06_excel_export.py`

The final stage converts the analytical pipeline outputs into a formatted Excel tab book.

The workbook is generated automatically from:

- the 28 cross-tab CSV files
- the tabulation plan
- significance-test results
- small-base QA
- final table-level QA

Final workbook:

```text
output/tab_books/Reach3_Social_Media_TabBook.xlsx
```

The workbook contains eight sheets:

1. `01_README`
2. `02_CONTENTS`
3. `03_METHODOLOGY`
4. `04_FACEBOOK`
5. `05_INSTAGRAM`
6. `06_X`
7. `07_TIKTOK`
8. `08_QA_SUMMARY`

The four platform sheets contain seven stacked tables each.

The Excel export includes:

- grouped demographic banner headers
- category comparison letters
- unweighted bases
- weighted percentages
- significance markers
- small-base flags
- methodological footnotes
- QA documentation

After saving, the export stage reopens the actual workbook and verifies all 28 table placements, 504 displayed bases, 1,512 displayed percentages, small-base notation, and stored significance letters. It confirms exactly 342 analytical cells receive one or more significance letters.

---

## Significance-Letter Interpretation

Within each demographic banner, categories are assigned letters such as A, B, C, and D.

When a percentage contains a letter, that percentage is statistically higher than the category represented by that letter at the 95% confidence level under the project's testing procedure.

For example:

```text
10.4% CD
```

indicates that the displayed percentage is significantly higher than the categories represented by C and D.

Categories with unweighted bases below 100 are excluded from significance testing.

---

## Quality Assurance

QA is built into each stage rather than performed only after tabulation.

The workflow validates:

- questionnaire routing
- analytical universes
- required variables
- response codes
- survey weights
- table structure
- percentage sums
- effective sample sizes
- pairwise-test uniqueness
- significance-test coverage
- low-base exclusions
- small-base classifications
- exported CSV structure
- final workbook structure
- persisted CSV base and percentage reconciliation
- Excel displayed-value and significance-marker reconciliation

The final pipeline produces:

```text
28 / 28 tables passing percentage QA
504 / 504 analytical percentage checks passing
1,596 pairwise tests validated
495 significant pairwise comparisons
342 analytical cells receiving significance markers
0 low-base categories entering significance testing
```

---

## Repository Structure

```text
Social-Media-Survey-Tabulation/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── documentation/
│   └── methodology.md
│
├── scripts/
│   └── python/
│       ├── 01_data_validation.py
│       ├── 02_variable_selection.py
│       ├── 03_tabulation_engine.py
│       ├── 04_significance_testing.py
│       ├── 05_final_qa.py
│       └── 06_excel_export.py
│
├── tabulation/
│   ├── tabulation_plan.csv
│   └── variable_selection_matrix.csv
│
├── output/
│   ├── tables/
│   │   ├── T01.csv
│   │   ├── ...
│   │   └── T28.csv
│   │
│   └── tab_books/
│       └── Reach3_Social_Media_TabBook.xlsx
│
└── qa/
    ├── effective_bases.csv
    ├── significance_test_results.csv
    ├── qa_summary.csv
    └── small_base_qa.csv
```

Raw survey data and original source documentation are maintained locally and excluded from version control.

---

## How to Run

The project was developed and validated using Python 3.11.

Install dependencies:

```bash
py -3.11 -m pip install -r requirements.txt
```

Place the W144 CSV at:

```text
data/raw/ATP_W144.csv
```

Then run the pipeline sequentially:

```bash
py -3.11 scripts/python/01_data_validation.py
py -3.11 scripts/python/02_variable_selection.py
py -3.11 scripts/python/03_tabulation_engine.py
py -3.11 scripts/python/04_significance_testing.py
py -3.11 scripts/python/05_final_qa.py
py -3.11 scripts/python/06_excel_export.py
```

A successful run regenerates the analytical tables, QA outputs, significance-testing results, and final Excel tab book.

---

## Methodology

Detailed methodological documentation is available in:

[`documentation/methodology.md`](documentation/methodology.md)

---

## Statistical Note

The significance tests in this project use weighted estimates and Kish-adjusted effective sample sizes.

They are intended to demonstrate a reproducible survey-tabulation and QA workflow and are not intended to reproduce Pew Research Center's exact complex-survey variance-estimation procedure, which cannot be reconstructed from the public-use variables and documentation used here.

No multiplicity adjustment is applied, so significance markers should be interpreted as exploratory.

---

## Portfolio Context

This project demonstrates practical survey-data processing skills relevant to market research and data-tabulation roles, including:

- questionnaire and routing interpretation
- survey-data validation
- tabulation planning
- weighted cross-tabulation
- demographic banner construction
- significance testing
- effective-base calculation
- small-base handling
- discrepancy investigation
- automated QA
- Excel tab-book production
- reproducible analytical documentation

The project emphasizes accuracy, reproducibility, and transparent QA from raw survey data through final client-style tabulation output.
