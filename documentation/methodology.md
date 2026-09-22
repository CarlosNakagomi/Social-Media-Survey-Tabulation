# Methodology

## Project Overview

This project reconstructs a professional end-to-end survey tabulation workflow using the Pew Research Center American Trends Panel Wave 144 (W144), conducted March 18–24, 2024.

The objective is to demonstrate a reproducible workflow for survey-data validation, variable selection, weighted cross-tabulation, effective-base calculation, significance testing, quality assurance, and automated Excel tab-book production.

The analytical question is:

> How do social-media usage motivations differ across Facebook, Instagram, X, and TikTok, and across demographic groups?

The project focuses on survey-processing methodology rather than substantive political analysis.

---

## Analytical Workflow

The workflow follows the sequence:

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

Six Python scripts implement the pipeline:

```text
01_data_validation.py
02_variable_selection.py
03_tabulation_engine.py
04_significance_testing.py
05_final_qa.py
06_excel_export.py
```

Each stage performs explicit validation before downstream outputs are produced.

---

## Data Source

The analysis uses the Pew Research Center American Trends Panel Wave 144 public-use dataset.

The analytical CSV contains:

- 10,454 respondent records
- 195 variables
- demographic variables
- social-media usage variables
- platform-specific user-motivation variables
- survey weights

The raw microdata and original source documentation are maintained locally and are not redistributed in the repository. The W144 public-use dataset must be obtained from the official Pew Research Center source.

For reproducibility, the expected raw-data location is:

```text
data/raw/ATP_W144.csv
```

---

## Analytical Scope

Four social-media platforms are included:

- Facebook
- Instagram
- X
- TikTok

Seven user motivations are analyzed for each platform:

1. Get news
2. Keep up with politics or political issues
3. Keep up with sports or pop culture
4. Entertainment
5. Keep up with friends and family
6. Connect with others who share your interests
7. Look at product reviews or recommendations

This produces 28 analytical variables and 28 cross-tab tables.

Table allocation:

```text
T01-T07   Facebook
T08-T14   Instagram
T15-T21   X
T22-T28   TikTok
```

---

## Data Validation

The first pipeline stage validates the analytical source before tabulation.

Validation includes:

- expected dataset dimensions
- presence of required variables
- platform usage variables
- platform frequency variables
- social-news variables
- demographic banner variables
- survey weights
- questionnaire routing
- derived Facebook/Instagram routing

The platform routing QA verifies that platform users and non-users are handled consistently in downstream questions.

Facebook and Instagram require additional routing validation because respondents using all four platforms were randomly assigned to one of those platform modules.

Derived routing logic is independently reconstructed and compared with the saved W144 derived variables before analysis proceeds.

All 28 WHY variables are also checked against their specified analytical
universes. Substantive responses and code `99` are prohibited outside the
routed universe; missing responses inside the universe are counted; and
unexpected or nonnumeric response codes cause validation to fail.

---

## Variable Selection

The analytical variable-selection stage identifies the 28 WHY variables used in the tab book.

Platform batteries are:

```text
FBWHY_a_W144 ... FBWHY_g_W144
IGWHY_a_W144 ... IGWHY_g_W144
XTWHY_a_W144 ... XTWHY_g_W144
TTWHY_a_W144 ... TTWHY_g_W144
```

Substantive response codes are:

```text
1 = Major reason
2 = Minor reason
3 = Not a reason
```

Special response code `99` is excluded from substantive percentage calculations.

The saved variable-selection matrix documents analytical inclusion and exclusion decisions.

Five primary demographic banners are retained:

```text
F_AGECAT
F_GENDER
F_EDUCCAT
F_CREGION
F_INC_TIER2
```

Secondary or more detailed demographic variables are excluded from the primary tab book to keep the deliverable focused.

---

## Analytical Universes

Platform-specific analytical universes are defined from questionnaire routing.

Facebook:

```text
DOV_ASKFB_W144 == 1
```

Instagram:

```text
DOV_ASKIG_W144 == 1
```

X:

```text
SMUSE_c_W144 == 1
```

TikTok:

```text
SMUSE_i_W144 == 1
```

Routing QA is performed before tabulation to verify that responses occur within the expected analytical universes.

---

## Survey Weighting

Weighted estimates use platform-specific W144 survey weights.

```text
Facebook   WEIGHT_W144_FB
Instagram  WEIGHT_W144_IG
X          WEIGHT_W144_XT
TikTok     WEIGHT_W144_TT
```

The overall W144 weight is retained for source-data validation but is not substituted for the platform-specific weights in the WHY tables.

Weighted percentages are calculated within the appropriate analytical universe and demographic category.

For each selected platform weight, QA verifies numeric and finite values,
strictly positive values for analytical respondents, and reports missing
weights within the analytical universe. Missing or invalid analytical
weights cause the pipeline to fail.

---

## Banner Definitions

Five demographic banners are used.

### Age

```text
18-29
30-49
50-64
65+
```

### Gender

```text
A man
A woman
In some other way
```

### Education

```text
College graduate+
Some College
H.S. graduate or less
```

### Region

```text
Northeast
Midwest
South
West
```

### Income

```text
Lower income
Middle income
Upper income
```

Together with the Total column, these produce 18 analytical columns per table:

```text
1 Total
4 Age
3 Gender
3 Education
4 Region
3 Income
----------------
18 columns
```

Non-substantive demographic response categories are excluded from the analytical banner columns.

---

## Tabulation Plan

The saved tabulation plan contains 28 rows, one for each platform-by-motivation table.

Each table definition identifies:

- table ID
- platform
- question battery
- analytical measure
- source variable
- response codes
- analytical universe
- survey weight
- banner variables
- display rules
- base requirements
- significance-testing requirements
- routing QA
- weight QA

This separates analytical specifications from the tabulation engine and makes the workflow easier to audit and reproduce.

---

## Weighted Cross-Tabulation

The tabulation engine generates T01 through T28 directly from the raw survey data and saved tabulation plan.

Each table contains four rows:

```text
Unweighted Base
Major reason
Minor reason
Not a reason
```

For each analytical column, the unweighted base is the number of valid substantive respondents in that category.

Weighted percentages are calculated as:

```text
Weighted percentage =
    weighted count for response
    /
    weighted valid-response base
    × 100
```

Only substantive WHY responses 1, 2, and 3 enter the percentage denominator.

The tabulation engine performs 504 percentage QA checks:

```text
28 tables × 18 analytical columns = 504 checks
```

For every analytical column:

```text
Major reason
+ Minor reason
+ Not a reason
≈ 100%
```

All 504 checks pass.

The generated analytical tables are exported to:

```text
output/tables/T01.csv
...
output/tables/T28.csv
```

---

## Effective Sample Size

Survey weighting can reduce the statistical information represented by a nominal unweighted sample size.

For each analytical table column, the project therefore calculates the Kish effective sample size:

$$
n_{\text{eff}}
=
\frac{\left(\sum_i w_i\right)^2}
{\sum_i w_i^2}
$$

where:

- \(w_i\) is the survey weight for respondent \(i\)
- \(n_{\text{eff}}\) is the Kish-adjusted effective sample size

A total of 504 effective-base records are calculated:

```text
28 tables × 18 analytical columns = 504
```

The results are exported to:

```text
qa/effective_bases.csv
```

---

## Significance Testing

Pairwise column-proportion tests are conducted within each demographic banner.

For two categories with weighted proportions \(p_1\) and \(p_2\), the project uses:

$$
SE
=
\sqrt{
\frac{p_1(1-p_1)}{n_{\text{eff},1}}
+
\frac{p_2(1-p_2)}{n_{\text{eff},2}}
}
$$

and:

$$
z
=
\frac{p_1-p_2}{SE}
$$

Two-sided p-values are calculated from the standard normal distribution.

Testing parameters:

```text
Alpha:                 0.05
Confidence level:      95%
Test type:             Two-sided
Minimum test base:     N = 100
Multiplicity control:  None
```

Categories with unweighted bases below 100 are excluded from significance testing.

Across the 28 tables, the pipeline generates:

```text
1,596 pairwise tests
495 significant comparisons at 95%
0 tests involving categories with N < 100
```

The complete test-level output is exported to:

```text
qa/significance_test_results.csv
```

---

## Significance Markers

The final Excel tab book converts significant pairwise comparisons into conventional category-letter markers.

Within each demographic banner, categories receive letters such as:

```text
A
B
C
D
```

When a significant comparison is identified, the letter of the category with the lower percentage is placed beside the higher percentage.

For example:

```text
10.4% CD
```

means the displayed percentage is significantly higher than the categories represented by C and D under the project's testing procedure.

Multiple significant pairwise comparisons can therefore produce multiple letters in a single analytical cell.

The 495 significant pairwise comparisons resolve to:

```text
342 unique analytical cells
```

receiving one or more significance letters.

The Excel-export stage explicitly reconciles these 342 cells against the significance-test results.

---

## Small-Base Rules

Base-size screening is performed independently from significance testing.

Rules:

```text
N >= 100        OK
30 <= N < 100   SMALL BASE
N < 30          VERY SMALL BASE
```

Display notation:

```text
*   N = 30-99
**  N < 30
```

The small-base QA covers the 17 demographic banner columns in each of 28 tables:

```text
28 × 17 = 476 banner cells
```

Final distribution:

| Classification | Cells |
|---|---:|
| N ≥ 100 | 448 |
| 30 ≤ N < 100 | 21 |
| N < 30 | 7 |
| Total | 476 |

All 28 cells below N=100 occur in:

```text
Gender | In some other way
```

No low-base category enters significance testing.

The screening results are exported to:

```text
qa/small_base_qa.csv
```

---

## Final Quality Assurance

The final QA stage independently rebuilds and validates key analytical outputs rather than relying only on upstream files.

QA includes:

### Table-Level QA

```text
28 / 28 tables pass
```

### Percentage QA

```text
Stage 03: 504 / 504 analytical percentage-sum checks pass
Stage 05: 1,512 / 1,512 persisted weighted percentages
          independently rebuilt and reconciled
Stage 05: 504 / 504 persisted unweighted bases
          independently rebuilt and reconciled
```

### Effective-Base QA

```text
504 / 504 effective-base records rebuilt and reconciled
```

### Small-Base QA

```text
476 / 476 demographic banner cells reviewed
448 adequate-base cells
21 small-base cells
7 very-small-base cells
```

### Significance QA

```text
1,596 significance tests validated
495 significant comparisons
0 low-base significance tests
342 unique Excel significance-marker cells
```

Table-level QA results are exported to:

```text
qa/qa_summary.csv
```

---

## Automated Excel Tab Book

The final pipeline stage creates the recruiter-ready Excel deliverable automatically.

Script:

```text
scripts/python/06_excel_export.py
```

Output:

```text
output/tab_books/Reach3_Social_Media_TabBook.xlsx
```

The workbook contains eight sheets:

```text
01_README
02_CONTENTS
03_METHODOLOGY
04_FACEBOOK
05_INSTAGRAM
06_X
07_TIKTOK
08_QA_SUMMARY
```

Each platform sheet contains seven stacked tables.

The workbook includes:

- grouped demographic banner headers
- category comparison letters
- unweighted bases
- weighted percentages
- significance markers
- small-base notation
- methodological footnotes
- QA summary

The export script performs round-trip workbook validation after saving the file. It reopens the saved XLSX and verifies all 28 table placements, 504 displayed bases, 1,512 displayed percentages, small-base notation, and the significance letters stored in the analytical cells.

It also reconciles the significance-marker logic against the statistical-test results and confirms:

```text
342 / 342 expected analytical marker cells
```

---

## Reproducibility

The project is implemented as a sequential six-script pipeline.

Install the required Python packages:

```bash
py -3.11 -m pip install -r requirements.txt
```

Place the raw W144 CSV at:

```text
data/raw/ATP_W144.csv
```

Then run:

```bash
py -3.11 scripts/python/01_data_validation.py
py -3.11 scripts/python/02_variable_selection.py
py -3.11 scripts/python/03_tabulation_engine.py
py -3.11 scripts/python/04_significance_testing.py
py -3.11 scripts/python/05_final_qa.py
py -3.11 scripts/python/06_excel_export.py
```

A successful complete run regenerates:

```text
output/tables/T01.csv ... T28.csv
qa/effective_bases.csv
qa/significance_test_results.csv
qa/qa_summary.csv
qa/small_base_qa.csv
output/tab_books/Reach3_Social_Media_TabBook.xlsx
```

---

## Methodological Limitations

The significance-testing procedure is designed as a transparent and reproducible portfolio implementation.

The public-use variables and documentation used for this project do not provide all design information required to reconstruct Pew Research Center's exact complex-survey variance-estimation procedure.

Therefore:

- weighted percentages use the supplied survey weights
- effective sample sizes use the Kish approximation
- pairwise tests use an independent weighted-proportion approximation
- categories with unweighted N below 100 are excluded from testing
- no multiplicity adjustment is applied
- significance results should be interpreted as exploratory

The significance markers should not be interpreted as an exact replication of Pew Research Center's internal statistical-testing methodology.

---

## Final Deliverables

The reproducible project produces three main classes of outputs.

### Analytical Tables

```text
output/tables/T01.csv ... T28.csv
```

### QA & Statistical Outputs

```text
qa/effective_bases.csv
qa/significance_test_results.csv
qa/qa_summary.csv
qa/small_base_qa.csv
```

### Final Tab Book

```text
output/tab_books/Reach3_Social_Media_TabBook.xlsx
```

Together, these outputs demonstrate the complete progression from raw survey data through validated analytical tables to a formatted client-style deliverable.
