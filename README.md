# Social Media Platform Usage & User Motivations

### Survey Tabulation, Statistical Testing & QA Workflow

A survey data processing and cross-tabulation portfolio project using Pew Research Center's American Trends Panel Wave 144 (W144).

This project demonstrates an end-to-end market research workflow: questionnaire interpretation, routing validation, analytical variable selection, tabulation planning, weighted cross-tabs, effective sample-size calculations, significance testing, automated QA, and production of a client-ready Excel tab book.

---

## Project Overview

This project analyzes how motivations for using **Facebook, Instagram, X, and TikTok** vary across demographic groups.

Rather than focusing only on final percentages, the project emphasizes the survey-processing workflow required to produce accurate, consistent, and auditable research tables.

The analytical workflow is:

**Questionnaire → Raw Survey Data → Data Validation → Variable Selection → Tabulation Plan → Banner Creation → Weighted Cross-Tabs → Effective Base Calculation → Significance Testing → QA → Excel Tab Book**

---

## Data Source

**Pew Research Center — American Trends Panel Wave 144 (W144)**  
Fieldwork: **March 18–24, 2024**

Analytical dataset:

- **10,454 records**
- **195 variables**
- **4 social media platforms**
- Platform-specific survey weights
- Demographic profile variables

The questionnaire, methodology, codebook, and public-use documentation were used to interpret survey routing, variable definitions, analytical universes, and weights.

The raw Pew Research Center microdata are **not redistributed in this repository**. Users who wish to reproduce the analysis should obtain the Wave 144 public-use dataset directly from Pew Research Center and place the CSV file at:

```text
data/raw/ATP_W144.csv
```

---

## Research Question

> How do social media usage patterns and motivations differ across Facebook, Instagram, X, and TikTok, and across demographic groups?

Seven platform-use motivations are analyzed:

1. Get news
2. Keep up with politics or political issues
3. Keep up with sports or pop culture
4. Entertainment
5. Keep up with friends and family
6. Connect with others who share your interests
7. Look at product reviews or recommendations

Across four platforms, this produces **28 analytical cross-tabs**.

---

## Project Highlights

| Component | Result |
|---|---:|
| Survey records | 10,454 |
| Source variables | 195 |
| Platforms analyzed | 4 |
| WHY measures | 28 |
| Cross-tab tables | 28 |
| Analytical columns per table | 18 |
| Table-column validations | 504 |
| Banner cells reviewed | 476 |
| Pairwise significance tests | 1,596 |
| Significant comparisons at 95% | 495 |
| Low-base significance tests | 0 |

---

## Survey Tabulation Workflow

### 1. Data Validation

The raw survey dataset is validated before analysis.

Checks include:

- expected dataset dimensions
- required analytical variables
- platform-use routing
- follow-up question routing
- Facebook/Instagram module assignment
- survey weight availability

This prevents structural questionnaire missingness from being incorrectly treated as respondent nonresponse.

### 2. Variable Selection

Variables are selected based on the research objective and questionnaire structure before statistical results are examined.

Candidate variables are screened using:

- questionnaire routing
- valid response availability
- missingness
- analytical universe
- usable base size
- cross-tab cell adequacy

The resulting analytical specification contains **28 WHY variables**.

### 3. Tabulation Plan

A formal tabulation specification defines:

- table ID
- platform
- analytical variable
- measure
- response codes
- universe
- survey weight
- banner variables
- display rules
- significance-testing requirements
- special-code handling

This separates analytical specifications from calculation logic and makes the tabulation workflow easier to audit.

### 4. Weighted Cross-Tabs

Each table contains:

- Total
- Age
- Gender
- Education
- Region
- Income

Weighted percentages are reported while displayed respondent bases remain unweighted.

Each table contains **18 analytical columns**, producing **504 table-column validation checks** across the 28 tables.

### 5. Effective Sample Size

Kish effective sample sizes are calculated to account for the loss of statistical precision associated with unequal survey weights.

These diagnostics are used in the project's significance-testing procedure rather than treating weighted observations as a simple random sample.

### 6. Significance Testing

Pairwise column-proportion tests are conducted within demographic banners using:

- weighted proportions
- Kish-adjusted effective sample sizes
- two-sided tests
- 95% confidence level
- minimum unweighted base of 100

The workflow evaluates **1,596 pairwise comparisons**.

Categories with fewer than 100 unweighted respondents are automatically excluded from significance testing.

### 7. QA & Discrepancy Validation

QA is embedded throughout the workflow rather than performed only after tables are produced.

Validation covers:

- questionnaire routing
- analytical universes
- response codes
- survey weights
- percentage calculations
- banner structure
- effective bases
- significance-test calculations
- small-base rules
- final table coverage

---

## QA & Validation

| QA Check | Result |
|---|---:|
| Cross-tabs validated | 28 / 28 PASS |
| Table-column percentage checks | 504 / 504 PASS |
| Effective-base records | 504 |
| Banner cells reviewed | 476 |
| Adequate bases (N ≥ 100) | 448 |
| Small bases (30 ≤ N < 100) | 21 |
| Very small bases (N < 30) | 7 |
| Significance tests reviewed | 1,596 |
| Tests involving N < 100 | **0** |

All **28 low-base banner cells** occurred in the `Gender | In some other way` category.

Small bases are flagged in the final tab book, and categories with N < 100 are excluded from significance testing.

---

## Final Deliverable

The primary recruiter/client-facing deliverable is:

**[`Reach3_Social_Media_TabBook.xlsx`](output/tab_books/Reach3_Social_Media_TabBook.xlsx)**

The Excel tab book contains:

- project documentation
- table of contents
- methodology
- Facebook tables
- Instagram tables
- X tables
- TikTok tables
- QA summary

Tables include unweighted bases, weighted percentages, demographic banners, significance indicators, and small-base warnings.

---

## Repository Structure

```text
Social-Media-Survey-Tabulation/
│
├── documentation/
│   └── methodology.md
│
├── output/
│   └── tab_books/
│       └── Reach3_Social_Media_TabBook.xlsx
│
├── qa/
│   ├── effective_bases.csv
│   ├── qa_summary.csv
│   ├── significance_test_results.csv
│   └── small_base_qa.csv
│
├── scripts/
│   └── python/
│       ├── 01_data_validation.py
│       ├── 02_variable_selection.py
│       ├── 03_tabulation_engine.py
│       ├── 04_significance_testing.py
│       └── 05_final_qa.py
│
├── tabulation/
│   ├── tabulation_plan.csv
│   └── variable_selection_matrix.csv
│
├── .gitignore
├── requirements.txt
└── README.md
```

The raw survey dataset and original source documentation are maintained locally and excluded from the public repository.

---

## Tools & Technologies

**Python**

- pandas
- NumPy

**Survey Analytics**

- questionnaire routing
- analytical universe definition
- survey weighting
- cross-tabulation
- demographic banner analysis
- Kish effective sample size
- column-proportion significance testing
- small-base management

**Reporting & QA**

- Microsoft Excel
- automated validation
- discrepancy reconciliation
- reproducible tabulation specifications
- audit-ready QA outputs

---

## How to Run

The project was validated using **Python 3.11**.

Install the required packages:

```bash
py -3.11 -m pip install -r requirements.txt
```

Obtain the Pew Research Center Wave 144 public-use dataset and save the CSV locally as:

```text
data/raw/ATP_W144.csv
```

Then run the analytical validation workflow sequentially:

```bash
py -3.11 scripts/python/01_data_validation.py
py -3.11 scripts/python/02_variable_selection.py
py -3.11 scripts/python/03_tabulation_engine.py
py -3.11 scripts/python/04_significance_testing.py
py -3.11 scripts/python/05_final_qa.py
```

A successful final validation ends with:

```text
FINAL QA VALIDATION PASSED
```

---

## Methodology

Detailed methodology — including routing rules, analytical universes, weighting, effective sample-size calculations, significance testing, small-base rules, QA procedures, and statistical limitations — is available here:

**[`documentation/methodology.md`](documentation/methodology.md)**

---

## Statistical Note

The significance-testing workflow uses weighted estimates and Kish-adjusted effective sample sizes.

It is an exploratory survey-tabulation procedure and is **not intended to reproduce Pew Research Center's exact complex-survey variance estimation**.

No multiplicity adjustment is applied to the pairwise comparisons.

---

## Portfolio Context

This project was developed as a portfolio demonstration of survey data processing and tabulation skills relevant to market research and research operations roles.

The emphasis is on **accuracy, reproducibility, QA, structured tabulation specifications, statistical testing, and production-ready research deliverables**.