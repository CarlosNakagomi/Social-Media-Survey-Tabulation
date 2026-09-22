\# Social Media Platform Usage \& User Motivations

\### Survey Tabulation, Statistical Testing \& QA Workflow



A survey data processing and cross-tabulation portfolio project using Pew Research Center's American Trends Panel Wave 144.



The project demonstrates an end-to-end market research workflow: questionnaire interpretation, routing validation, analytical variable selection, tabulation planning, weighted cross-tabs, effective sample-size calculations, significance testing, automated QA, and production of a client-ready Excel tab book.



\---



\## Project Overview



This project analyzes how motivations for using \*\*Facebook, Instagram, X, and TikTok\*\* vary across demographic groups.



Rather than focusing only on final percentages, the project emphasizes the survey-processing workflow required to produce accurate and auditable research tables.



The analytical pipeline is:



\*\*Questionnaire → Raw Survey Data → Data Validation → Variable Selection → Tabulation Plan → Banner Creation → Weighted Cross-Tabs → Effective Base Calculation → Significance Testing → QA → Excel Tab Book\*\*



\---



\## Data Source



\*\*Pew Research Center — American Trends Panel Wave 144 (W144)\*\*  

Fieldwork: \*\*March 18–24, 2024\*\*



Analytical dataset:



\- \*\*10,454 records\*\*

\- \*\*195 variables\*\*

\- Four social media platforms

\- Platform-specific survey weights

\- Demographic profile variables



The questionnaire, methodology, codebook, and public-use data documentation were used to interpret survey routing, variable definitions, analytical universes, and weights.



\---



\## Research Question



> How do social media usage patterns and motivations differ across Facebook, Instagram, X, and TikTok, and across demographic groups?



Seven platform-use motivations are analyzed:



1\. Get news

2\. Keep up with politics or political issues

3\. Keep up with sports or pop culture

4\. Entertainment

5\. Keep up with friends and family

6\. Connect with others who share your interests

7\. Look at product reviews or recommendations



Across four platforms, this produces \*\*28 analytical cross-tabs\*\*.



\---



\## Project Highlights



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



\---



\## Survey Tabulation Workflow



\### 1. Data Validation



The raw survey dataset is validated before analysis.



Checks include:



\- expected dataset dimensions

\- required analytical variables

\- platform-use routing

\- follow-up question routing

\- Facebook/Instagram module assignment

\- survey weight availability



This prevents structural questionnaire missingness from being incorrectly treated as respondent nonresponse.



\### 2. Variable Selection



Variables are selected based on the research objective and questionnaire structure before statistical results are examined.



Candidate variables are screened using:



\- routing

\- valid response availability

\- missingness

\- analytical universe

\- usable base size

\- cross-tab cell adequacy



The resulting analytical specification contains \*\*28 WHY variables\*\*.



\### 3. Tabulation Plan



A formal tabulation specification defines:



\- table ID

\- platform

\- analytical variable

\- measure

\- response codes

\- universe

\- survey weight

\- banner variables

\- display rules

\- significance-testing requirements

\- special-code handling



This separates analytical specifications from calculation logic.



\### 4. Weighted Cross-Tabs



Each table contains:



\- Total

\- Age

\- Gender

\- Education

\- Region

\- Income



Weighted percentages are reported while respondent bases remain unweighted.



Each table contains \*\*18 analytical columns\*\*, producing \*\*504 table-column validation checks\*\* across the 28 tables.



\### 5. Effective Sample Size



Kish effective sample sizes are calculated to account for precision loss associated with unequal survey weights.



These diagnostics are used in the project's significance-testing procedure and provide a more appropriate precision estimate than treating weighted observations as a simple random sample.



\### 6. Significance Testing



Pairwise column-proportion tests are conducted within demographic banners using:



\- weighted proportions

\- Kish-adjusted effective sample sizes

\- two-sided tests

\- 95% confidence level

\- minimum unweighted base of 100



The pipeline evaluated \*\*1,596 pairwise comparisons\*\*.



Categories with fewer than 100 unweighted respondents are automatically excluded from testing.



\### 7. QA \& Discrepancy Validation



QA is embedded throughout the workflow rather than performed only after tables are produced.



The final validation covered:



\- questionnaire routing

\- analytical universes

\- response codes

\- survey weights

\- percentage calculations

\- banner structure

\- effective bases

\- significance-test calculations

\- small-base rules

\- final table coverage



\---



\## QA \& Validation



Final QA results:



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

| Tests involving N < 100 | \*\*0\*\* |



All \*\*28 low-base banner cells\*\* occurred in the `Gender | In some other way` category.



Small bases are automatically flagged in the final tab book and excluded from significance testing where N < 100.



\---



\## Final Deliverable



The primary recruiter/client-facing deliverable is:



\*\*`output/tab\_books/Reach3\_Social\_Media\_TabBook.xlsx`\*\*



The Excel tab book contains:



\- project documentation

\- table of contents

\- methodology

\- Facebook tables

\- Instagram tables

\- X tables

\- TikTok tables

\- QA summary



Tables include unweighted bases, weighted percentages, demographic banners, significance indicators, and small-base warnings.



\---



\## Repository Structure



```text

Reach3/

│

├── data/

│   └── raw/

│

├── docs/

│   ├── ATP\_W144\_Codebook.xlsx

│   ├── ATP\_W144\_Methodology.pdf

│   ├── ATP\_W144\_Questionnaire.pdf

│   └── ATP\_W144\_Readme.txt

│

├── documentation/

│   └── methodology.md

│

├── output/

│   └── tab\_books/

│       └── Reach3\_Social\_Media\_TabBook.xlsx

│

├── qa/

│   ├── effective\_bases.csv

│   ├── qa\_summary.csv

│   ├── significance\_test\_results.csv

│   └── small\_base\_qa.csv

│

├── scripts/

│   └── python/

│       ├── 01\_data\_validation.py

│       ├── 02\_variable\_selection.py

│       ├── 03\_tabulation\_engine.py

│       ├── 04\_significance\_testing.py

│       └── 05\_final\_qa.py

│

├── tabulation/

│   ├── tabulation\_plan.csv

│   └── variable\_selection\_matrix.csv

│

├── .gitignore

├── requirements.txt

└── README.md

```



\---



\## Tools \& Technologies



\*\*Python\*\*



\- pandas

\- NumPy



\*\*Survey Analytics\*\*



\- questionnaire routing

\- analytical universe definition

\- survey weighting

\- cross-tabulation

\- banner analysis

\- Kish effective sample size

\- column-proportion significance testing

\- small-base management



\*\*Reporting \& QA\*\*



\- Microsoft Excel

\- automated validation

\- discrepancy reconciliation

\- reproducible tabulation specifications



\---



\## How to Run



The project was validated using \*\*Python 3.11\*\*.



Install the required packages:



```bash

py -3.11 -m pip install -r requirements.txt

```



Run the analytical validation pipeline sequentially:



```bash

py -3.11 scripts/python/01\_data\_validation.py

py -3.11 scripts/python/02\_variable\_selection.py

py -3.11 scripts/python/03\_tabulation\_engine.py

py -3.11 scripts/python/04\_significance\_testing.py

py -3.11 scripts/python/05\_final\_qa.py

```



A successful run ends with:



```text

FINAL QA VALIDATION PASSED

```



\---



\## Methodology



Detailed methodology, including routing rules, analytical universes, weighting, effective sample-size calculations, significance testing, small-base rules, QA procedures, and statistical limitations, is available in:



\*\*\[`documentation/methodology.md`](documentation/methodology.md)\*\*



\---



\## Statistical Note



The significance-testing workflow uses weighted estimates and Kish-adjusted effective sample sizes.



It is designed as an exploratory survey-tabulation procedure and is \*\*not intended to reproduce Pew Research Center's exact complex-survey variance estimation\*\*.



No multiplicity adjustment is applied to the pairwise comparisons.



\---



\## Portfolio Context



This project was developed as a portfolio demonstration of survey data processing and tabulation skills relevant to market research and research operations roles.



The emphasis is on \*\*accuracy, reproducibility, QA, structured tabulation specifications, statistical testing, and production-ready research deliverables\*\*.

