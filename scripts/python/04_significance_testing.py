"""
04_significance_testing.py

Calculates effective sample sizes and weighted pairwise
significance tests for the W144 Social Media Platform Usage
& User Motivations study.

Method:
- Weighted proportions
- Kish effective sample size
- Two-sided independent proportion tests
- 95% confidence level
- Unweighted N < 100 excluded from significance testing

Outputs:
- qa/effective_bases.csv
- qa/significance_test_results.csv

IMPORTANT:
These tests are an analytical approximation for portfolio
purposes and are not intended to reproduce Pew Research
Center's exact complex-survey variance estimation procedure.
"""

from pathlib import Path
from itertools import combinations
from math import sqrt
from statistics import NormalDist
import re

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT / "data" / "raw" / "ATP_W144.csv"
)

PLAN_PATH = (
    PROJECT_ROOT / "tabulation" / "tabulation_plan.csv"
)

QA_DIR = PROJECT_ROOT / "qa"
QA_DIR.mkdir(parents=True, exist_ok=True)

EFFECTIVE_BASE_PATH = (
    QA_DIR / "effective_bases.csv"
)

SIGNIFICANCE_PATH = (
    QA_DIR / "significance_test_results.csv"
)


# ============================================================
# SETTINGS
# ============================================================

VALID_RESPONSES = [1, 2, 3]

RESPONSE_LABELS = {
    1: "Major reason",
    2: "Minor reason",
    3: "Not a reason",
}

ALPHA = 0.05
MIN_TEST_BASE = 100

NORMAL = NormalDist()


# ============================================================
# BANNERS
# ============================================================

banner_definitions = {
    "F_AGECAT": {
        1: "18-29",
        2: "30-49",
        3: "50-64",
        4: "65+",
    },
    "F_GENDER": {
        1: "A man",
        2: "A woman",
        3: "In some other way",
    },
    "F_EDUCCAT": {
        1: "College graduate+",
        2: "Some College",
        3: "H.S. graduate or less",
    },
    "F_CREGION": {
        1: "Northeast",
        2: "Midwest",
        3: "South",
        4: "West",
    },
    "F_INC_TIER2": {
        1: "Lower income",
        2: "Middle income",
        3: "Upper income",
    },
}

banner_names = {
    "F_AGECAT": "Age",
    "F_GENDER": "Gender",
    "F_EDUCCAT": "Education",
    "F_CREGION": "Region",
    "F_INC_TIER2": "Income",
}


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)
plan = pd.read_csv(PLAN_PATH)

print("=" * 72)
print("W144 SIGNIFICANCE TESTING")
print("=" * 72)

print(
    f"\nRaw data: {df.shape[0]:,} rows x "
    f"{df.shape[1]:,} columns"
)
print(f"Tabulation plan: {len(plan)} tables")


# ============================================================
# BASIC VALIDATION
# ============================================================

assert len(plan) == 28
assert plan["table_id"].nunique() == 28
assert plan["variable"].nunique() == 28

print("\n[PASS] Tabulation plan structure")


# ============================================================
# UNIVERSE PARSER
# ============================================================

def parse_universe(expression):

    pattern = (
        r"^\s*([A-Za-z0-9_]+)"
        r"\s*==\s*(-?\d+(?:\.\d+)?)\s*$"
    )

    match = re.match(
        pattern,
        str(expression)
    )

    if not match:
        raise ValueError(
            f"Unsupported universe: {expression}"
        )

    variable = match.group(1)
    value = float(match.group(2))

    if variable not in df.columns:
        raise KeyError(
            f"Universe variable not found: {variable}"
        )

    return (
        pd.to_numeric(
            df[variable],
            errors="coerce"
        )
        == value
    )


# ============================================================
# KISH EFFECTIVE SAMPLE SIZE
# ============================================================

def kish_effective_n(weights):

    weights = pd.to_numeric(
        weights,
        errors="coerce"
    ).dropna()

    if len(weights) == 0:
        return np.nan

    sum_w = weights.sum()
    sum_w2 = (weights ** 2).sum()

    if sum_w2 == 0:
        return np.nan

    return (sum_w ** 2) / sum_w2


# ============================================================
# CATEGORY STATISTICS
# ============================================================

def category_statistics(
    data,
    outcome,
    weight,
    banner_var=None,
    banner_code=None,
):

    subset = data

    if banner_var is not None:
        subset = subset.loc[
            subset[banner_var] == banner_code
        ]

    valid = (
        subset[outcome].isin(VALID_RESPONSES)
        & subset[weight].notna()
    )

    subset = subset.loc[valid].copy()

    n = len(subset)

    if n == 0:
        return {
            "n": 0,
            "effective_n": np.nan,
            "percentages": {
                response: np.nan
                for response in VALID_RESPONSES
            },
        }

    weights = subset[weight]

    effective_n = kish_effective_n(weights)

    denominator = weights.sum()

    percentages = {}

    for response in VALID_RESPONSES:

        numerator = subset.loc[
            subset[outcome] == response,
            weight,
        ].sum()

        percentages[response] = (
            numerator / denominator * 100
        )

    return {
        "n": n,
        "effective_n": effective_n,
        "percentages": percentages,
    }


# ============================================================
# PAIRWISE PROPORTION TEST
# ============================================================

def pairwise_prop_test(
    pct_1,
    pct_2,
    effective_n_1,
    effective_n_2,
):

    p1 = pct_1 / 100
    p2 = pct_2 / 100

    variance = (
        p1 * (1 - p1) / effective_n_1
        +
        p2 * (1 - p2) / effective_n_2
    )

    if variance <= 0:
        return np.nan, np.nan, False

    se = sqrt(variance)

    z = (p1 - p2) / se

    p_value = (
        2
        * (
            1
            - NORMAL.cdf(abs(z))
        )
    )

    significant = p_value < ALPHA

    return z, p_value, significant


# ============================================================
# BUILD EFFECTIVE BASES
# ============================================================

effective_base_rows = []
table_stats = {}

for _, plan_row in plan.iterrows():

    table_id = plan_row["table_id"]
    platform = plan_row["platform"]
    outcome = plan_row["variable"]
    weight = plan_row["weight"]

    if outcome not in df.columns:
        raise KeyError(
            f"{table_id}: outcome not found: {outcome}"
        )

    if weight not in df.columns:
        raise KeyError(
            f"{table_id}: weight not found: {weight}"
        )

    universe = parse_universe(
        plan_row["universe"]
    )

    data = df.loc[universe].copy()

    table_stats[table_id] = {}

    # TOTAL
    stats = category_statistics(
        data,
        outcome,
        weight,
    )

    weighting_deff = (
        stats["n"] / stats["effective_n"]
        if stats["effective_n"] > 0
        else np.nan
    )

    effective_base_rows.append({
        "table_id": table_id,
        "platform": platform,
        "banner": "Total",
        "category": "Total",
        "unweighted_n": stats["n"],
        "effective_n": stats["effective_n"],
        "weighting_deff": weighting_deff,
    })

    # BANNERS
    for banner_var, categories in (
        banner_definitions.items()
    ):

        banner = banner_names[banner_var]

        table_stats[table_id][banner] = {}

        for code, category in categories.items():

            stats = category_statistics(
                data,
                outcome,
                weight,
                banner_var,
                code,
            )

            table_stats[
                table_id
            ][banner][category] = stats

            weighting_deff = (
                stats["n"] / stats["effective_n"]
                if stats["effective_n"] > 0
                else np.nan
            )

            effective_base_rows.append({
                "table_id": table_id,
                "platform": platform,
                "banner": banner,
                "category": category,
                "unweighted_n": stats["n"],
                "effective_n": stats["effective_n"],
                "weighting_deff": weighting_deff,
            })


effective_bases = pd.DataFrame(
    effective_base_rows
)

assert len(effective_bases) == 504

assert (
    effective_bases[
        ["table_id", "platform", "banner", "category"]
    ]
    .duplicated()
    .sum()
    == 0
)

print(
    "[PASS] Effective bases calculated "
    "(504/504)"
)


# ============================================================
# MEASURE LABELS
# ============================================================

MEASURE_LABELS = {
    "a": "Get news",
    "b": "Keep up with politics or political issues",
    "c": "Keep up with sports or pop culture",
    "d": "Entertainment",
    "e": "Keep up with friends and family",
    "f": "Connect with others who share your interests",
    "g": "Look at product reviews or recommendations",
}


def get_measure_label(variable):

    match = re.search(
        r"WHY_([a-g])_W144$",
        str(variable)
    )

    if not match:
        raise ValueError(
            "Unable to determine WHY item from "
            f"variable: {variable}"
        )

    return MEASURE_LABELS[
        match.group(1)
    ]


# ============================================================
# PAIRWISE TESTS
# ============================================================

test_rows = []

for _, plan_row in plan.iterrows():

    table_id = plan_row["table_id"]
    platform = plan_row["platform"]
    variable = plan_row["variable"]

    measure = get_measure_label(variable)

    for banner, categories in (
        table_stats[table_id].items()
    ):

        eligible_categories = [
            category
            for category in categories
            if (
                categories[category]["n"]
                >= MIN_TEST_BASE
            )
        ]

        for category_1, category_2 in combinations(
            eligible_categories,
            2,
        ):

            stats_1 = categories[category_1]
            stats_2 = categories[category_2]

            for response_code in VALID_RESPONSES:

                pct_1 = (
                    stats_1["percentages"][
                        response_code
                    ]
                )

                pct_2 = (
                    stats_2["percentages"][
                        response_code
                    ]
                )

                z, p_value, significant = (
                    pairwise_prop_test(
                        pct_1,
                        pct_2,
                        stats_1["effective_n"],
                        stats_2["effective_n"],
                    )
                )

                test_rows.append({
                    "table_id": table_id,
                    "platform": platform,
                    "measure": measure,
                    "banner": banner,
                    "response":
                        RESPONSE_LABELS[
                            response_code
                        ],
                    "category_1": category_1,
                    "category_2": category_2,
                    "pct_1": pct_1,
                    "pct_2": pct_2,
                    "n_1": stats_1["n"],
                    "n_2": stats_2["n"],
                    "effective_n_1":
                        stats_1["effective_n"],
                    "effective_n_2":
                        stats_2["effective_n"],
                    "difference_pp":
                        pct_1 - pct_2,
                    "z": z,
                    "p_value": p_value,
                    "significant_95": significant,
                })


sig_results = pd.DataFrame(test_rows)

print(
    f"[PASS] Pairwise tests generated: "
    f"{len(sig_results):,}"
)


# ============================================================
# TEST COUNT QA
# ============================================================

assert len(sig_results) == 1596, (
    f"Expected 1,596 tests; "
    f"found {len(sig_results):,}"
)

print("[PASS] Expected 1,596 tests")


# ============================================================
# SIGNIFICANT COUNT QA
# ============================================================

significant_count = int(
    sig_results["significant_95"].sum()
)

assert significant_count == 495, (
    f"Expected 495 significant tests; "
    f"found {significant_count}"
)

print(
    "[PASS] 495 significant comparisons "
    "at 95% confidence"
)


# ============================================================
# LOW-BASE EXCLUSION QA
# ============================================================

low_base_tests = sig_results.loc[
    (sig_results["n_1"] < MIN_TEST_BASE)
    |
    (sig_results["n_2"] < MIN_TEST_BASE)
]

assert low_base_tests.empty, (
    "At least one N < 100 category entered "
    "significance testing."
)

print(
    "[PASS] No N < 100 categories "
    "entered significance testing"
)


# ============================================================
# KEY UNIQUENESS QA
# ============================================================

comparison_keys = [
    "table_id",
    "platform",
    "measure",
    "banner",
    "response",
    "category_1",
    "category_2",
]

duplicate_count = int(
    sig_results.duplicated(
        comparison_keys
    ).sum()
)

assert duplicate_count == 0, (
    f"Generated results contain "
    f"{duplicate_count} duplicate keys."
)

print(
    "[PASS] Significance-test keys are unique"
)


# ============================================================
# COVERAGE QA
# ============================================================

expected_platforms = {
    "Facebook",
    "Instagram",
    "X",
    "TikTok",
}

actual_platforms = set(
    sig_results["platform"].unique()
)

assert actual_platforms == expected_platforms, (
    f"Unexpected platform set: {actual_platforms}"
)

expected_responses = {
    "Major reason",
    "Minor reason",
    "Not a reason",
}

actual_responses = set(
    sig_results["response"].unique()
)

assert actual_responses == expected_responses, (
    f"Unexpected response set: {actual_responses}"
)

assert (
    sig_results["measure"].nunique()
    == 7
), (
    "Expected seven WHY measures"
)

assert sig_results["table_id"].nunique() == 28

print(
    "[PASS] Platform, response, measure "
    "and table coverage validated"
)


# ============================================================
# EXPORT OUTPUTS
# ============================================================

effective_bases.to_csv(
    EFFECTIVE_BASE_PATH,
    index=False,
    float_format="%.12g",
)

sig_results.to_csv(
    SIGNIFICANCE_PATH,
    index=False,
    float_format="%.12g",
)

assert EFFECTIVE_BASE_PATH.exists()
assert SIGNIFICANCE_PATH.exists()

print(
    "[PASS] Effective bases exported to "
    "qa/effective_bases.csv"
)

print(
    "[PASS] Significance results exported to "
    "qa/significance_test_results.csv"
)


# ============================================================
# ROUND-TRIP OUTPUT QA
# ============================================================

saved_bases = pd.read_csv(
    EFFECTIVE_BASE_PATH
)

saved_sig = pd.read_csv(
    SIGNIFICANCE_PATH
)

assert len(saved_bases) == 504
assert len(saved_sig) == 1596

assert (
    saved_sig["significant_95"]
    .astype(str)
    .str.lower()
    .eq("true")
    .sum()
    == 495
)

assert (
    (
        saved_sig["n_1"] < MIN_TEST_BASE
    )
    |
    (
        saved_sig["n_2"] < MIN_TEST_BASE
    )
).sum() == 0

print(
    "[PASS] Exported QA files passed "
    "round-trip validation"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "-" * 72)
print("SIGNIFICANCE TESTING SUMMARY")
print("-" * 72)

print(
    f"Effective-base records: "
    f"{len(effective_bases):,}"
)

print(
    f"Pairwise tests:          "
    f"{len(sig_results):,}"
)

print(
    f"Significant at 95%:      "
    f"{significant_count:,}"
)

print(
    f"Minimum test base:       "
    f"{MIN_TEST_BASE}"
)

print(
    "Multiplicity adjustment: None "
    "(exploratory)"
)


# ============================================================
# T01 PREVIEW
# ============================================================

print("\nT01 first five tests:")

print(
    sig_results.loc[
        sig_results["table_id"] == "T01"
    ]
    .head(5)
    .to_string(index=False)
)


# ============================================================
# METHODOLOGY NOTE
# ============================================================

print("\nMethodology note:")

print(
    "Pairwise column-proportion tests use weighted estimates "
    "and Kish-adjusted effective sample sizes. Tests are "
    "two-sided at the 95% confidence level. Categories with "
    "unweighted bases below 100 are excluded from significance "
    "testing. No multiplicity adjustment is applied."
)

print(
    "These tests are exploratory and are not intended to "
    "reproduce Pew Research Center's exact complex-survey "
    "variance-estimation procedure."
)


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 72)
print("SIGNIFICANCE TESTING PASSED AND OUTPUTS EXPORTED")
print("=" * 72)