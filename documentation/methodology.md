# Methodology

## Project Overview

This project reconstructs a professional survey-tabulation workflow using the Pew Research Center American Trends Panel Wave 144 (W144), conducted March 18–24, 2024.

The analysis examines how motivations for using Facebook, Instagram, X, and TikTok vary across demographic groups.

The workflow was designed to demonstrate survey data preparation, questionnaire routing validation, weighted cross-tabulation, significance testing, base-size QA, discrepancy investigation, and production of a client-ready Excel tab book.

---

## Analytical Workflow

The project follows the workflow:

**Questionnaire → Raw Survey Data → Data Validation → Variable Selection → Tabulation Plan → Banner Creation → Weighted Cross-Tabs → Effective Base Calculation → Significance Testing → QA → Excel Tab Book**

Five reproducible Python scripts implement the analytical and QA stages:

1. `01_data_validation.py`
2. `02_variable_selection.py`
3. `03_tabulation_engine.py`
4. `04_significance_testing.py`
5. `05_final_qa.py`

Each stage contains automated validation checks and fails when expected analytical conditions are not met.

---

## Data Source

The analysis uses the Pew Research Center American Trends Panel Wave 144 public-use dataset.

The survey was conducted March 18–24, 2024.

The analytical dataset contains:

- **10,454 records**
- **195 variables**

The project uses survey responses related to four social media platforms:

- Facebook
- Instagram
- X
- TikTok

Supporting questionnaire, methodology, codebook, and readme documentation were used to interpret variable definitions, survey routing, and weighting.

---

## Research Question

The primary analytical question is:

> How do social media usage patterns and motivations differ across Facebook, Instagram, X, and TikTok, and across demographic groups?

The tabulation analysis focuses on seven motivations for platform use:

1. Get news
2. Keep up with politics or political issues
3. Keep up with sports or pop culture
4. Entertainment
5. Keep up with friends and family
6. Connect with others who share your interests
7. Look at product reviews or recommendations

Each motivation uses three substantive response categories:

- Major reason
- Minor reason
- Not a reason

Special/non-substantive response codes are excluded from percentage bases.

---

## Variable Selection

Variables were selected a priori based on the research objective and questionnaire structure rather than observed statistical significance.

Candidate variables were then screened for analytical feasibility using:

- questionnaire routing
- valid response availability
- missingness
- analytical universe
- usable base size
- cross-tab cell adequacy

The final analytical specification contains **28 WHY variables**:

- 7 Facebook measures
- 7 Instagram measures
- 7 X measures
- 7 TikTok measures

A reproducible variable-selection matrix is stored in:

`tabulation/variable_selection_matrix.csv`

---

## Questionnaire Routing

Survey routing was explicitly validated before tabulation.

Platform-use variables determine which respondents were eligible for subsequent platform-specific questions.

Facebook and Instagram include additional routing because respondents who used all four studied platforms were randomly assigned to either the Facebook or Instagram module.

The analytical universes are:

| Platform | Universe |
|---|---|
| Facebook | `DOV_ASKFB_W144 == 1` |
| Instagram | `DOV_ASKIG_W144 == 1` |
| X | `SMUSE_c_W144 == 1` |
| TikTok | `SMUSE_i_W144 == 1` |

Routing QA confirmed that platform-use, follow-up, and WHY variables behaved consistently with their expected analytical universes.

Raw missingness is therefore not interpreted as item nonresponse without first accounting for questionnaire routing.

---

## Weighting

Platform-specific survey weights are used for analytical estimates:

| Platform | Weight |
|---|---|
| Facebook | `WEIGHT_W144_FB` |
| Instagram | `WEIGHT_W144_IG` |
| X | `WEIGHT_W144_XT` |
| TikTok | `WEIGHT_W144_TT` |

Weighted percentages are reported in the cross-tabs, while displayed sample bases are unweighted respondent counts.

This distinction preserves both population-representative estimation and transparency regarding the number of respondents supporting each estimate.

---

## Banner Variables

Five primary demographic banners are used.

### Age

- 18–29
- 30–49
- 50–64
- 65+

### Gender

- A man
- A woman
- In some other way

### Education

- College graduate+
- Some College
- H.S. graduate or less

### Region

- Northeast
- Midwest
- South
- West

### Income

- Lower income
- Middle income
- Upper income

Non-substantive banner responses are excluded from analytical banner columns.

Each table therefore contains:

- 1 Total column
- 17 demographic banner columns

for **18 analytical columns per table**.

---

## Tabulation Plan

The project contains **28 cross-tab tables**, identified as `T01` through `T28`.

The tabulation plan explicitly defines for each table:

- table ID
- platform
- questionnaire item
- analytical variable
- measure
- response codes
- universe
- survey weight
- banner variables
- display convention
- significance-testing requirement
- special-code handling
- routing QA
- weighting QA

The specification is stored in:

`tabulation/tabulation_plan.csv`

This separates analytical specifications from calculation logic and makes the tabulation process auditable.

---

## Weighted Cross-Tabulation

For each table, the tabulation engine:

1. applies the defined analytical universe;
2. retains substantive response codes;
3. applies the appropriate platform weight;
4. calculates the unweighted base;
5. calculates weighted percentages;
6. produces Total and demographic banner columns;
7. validates the resulting percentage distributions.

The final engine generated:

- **28 tables**
- **18 analytical columns per table**
- **504 table-column QA checks**

All **504 of 504** percentage checks passed.

---

## Effective Sample Size

Because unequal survey weights reduce statistical precision, Kish effective sample sizes are calculated.

The effective sample size is:

\[
n_{eff} =
\frac{(\sum w_i)^2}
{\sum w_i^2}
\]

where \(w_i\) represents the survey weight for respondent \(i\).

A weighting design-effect diagnostic is also calculated as:

\[
DEFF_w =
\frac{n}{n_{eff}}
\]

These diagnostics represent the unequal-weighting component of design effect and are not a reconstruction of the survey's full complex-sample design.

---

## Significance Testing

Pairwise column-proportion tests are conducted within each demographic banner.

Tests use:

- weighted proportions
- Kish-adjusted effective sample sizes
- two-sided tests
- 95% confidence level
- minimum unweighted base of 100

For two proportions \(p_1\) and \(p_2\), the standard error is approximated as:

\[
SE =
\sqrt{
\frac{p_1(1-p_1)}{n_{eff,1}}
+
\frac{p_2(1-p_2)}{n_{eff,2}}
}
\]

and:

\[
z =
\frac{p_1-p_2}{SE}
\]

Categories with an unweighted base below 100 are excluded from significance testing.

The testing engine generated:

- **1,596 pairwise comparisons**
- **495 comparisons significant at the 95% confidence level**
- **0 tests involving categories with N < 100**

No multiplicity adjustment is applied. Significance markers should therefore be interpreted as exploratory.

These tests are not intended to reproduce Pew Research Center's exact complex-survey variance-estimation procedure because the required design information is not reconstructed from the public-use materials used in this project.

---

## Small-Base Rules

Every demographic banner column is screened using its unweighted base.

The reporting rules are:

| Unweighted Base | Treatment |
|---:|---|
| N ≥ 100 | OK |
| 30 ≤ N < 100 | `*` SMALL BASE |
| N < 30 | `**` VERY SMALL BASE |

Across the **476 demographic banner cells**:

- **448** had N ≥ 100
- **21** were SMALL BASE
- **7** were VERY SMALL BASE

All 28 cells below N=100 occurred in:

`Gender | In some other way`

No low-base category was included in significance testing.

---

## Quality Assurance

QA is performed at multiple stages rather than only after table production.

Checks include:

- dataset dimensions
- required-variable availability
- questionnaire routing
- analytical universes
- response-code validation
- variable-selection reconciliation
- weight assignment
- weighted percentage calculations
- banner structure
- effective sample sizes
- significance-test eligibility
- pairwise significance calculations
- small-base identification
- final table coverage

The final QA results include:

| QA Metric | Result |
|---|---:|
| Tables | 28 |
| Percentage QA | 28/28 PASS |
| Effective-base records | 504 |
| Banner cells reviewed | 476 |
| Adequate bases | 448 |
| Small bases | 21 |
| Very small bases | 7 |
| Pairwise significance tests | 1,596 |
| Low-base significance tests | 0 |

Intermediate QA outputs are retained in the `qa/` directory to provide an audit trail.

---

## Deliverable

The final reporting deliverable is:

`output/tab_books/Reach3_Social_Media_TabBook.xlsx`

The workbook contains:

- project documentation
- contents
- methodology
- Facebook tables
- Instagram tables
- X tables
- TikTok tables
- QA summary

Tables display unweighted bases, weighted percentages, demographic banners, small-base flags, and significance indicators.

---

## Reproducibility

The analytical workflow is implemented as sequential Python scripts.

Run:

```bash
py -3.11 scripts/python/01_data_validation.py
py -3.11 scripts/python/02_variable_selection.py
py -3.11 scripts/python/03_tabulation_engine.py
py -3.11 scripts/python/04_significance_testing.py
py -3.11 scripts/python/05_final_qa.py
```

All five stages must complete successfully for the reconstructed analytical workflow to be considered validated.

---

## Methodological Limitations

This project is a portfolio implementation based on a public-use survey dataset.

The significance-testing procedure uses Kish-adjusted effective sample sizes as an approximation for variance estimation. It does not reproduce all components of the original survey's complex sampling and weighting design.

The significance results should therefore be interpreted as exploratory analytical indicators rather than exact replications of Pew Research Center statistical testing.

No multiplicity correction is applied to the pairwise comparisons.