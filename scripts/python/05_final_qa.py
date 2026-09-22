"""
05_final_qa.py

Final QA layer for the W144 Social Media Platform Usage &
User Motivations survey-tabulation project.

Validates:
1. Table-level analytical universes and valid bases.
2. Weighted bases.
3. Percentage QA status.
4. Banner-category base reconciliation.
5. Small-base / very-small-base flags.
6. Exclusion of N < 100 categories from significance testing.
7. Reconciliation with previously approved QA outputs.

Small-base convention:
    N < 30      -> ** VERY SMALL BASE
    30 <= N < 100 -> * SMALL BASE
    N >= 100    -> OK
"""

from pathlib import Path
import re

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ATP_W144.csv"
)

PLAN_PATH = (
    PROJECT_ROOT
    / "tabulation"
    / "tabulation_plan.csv"
)

REFERENCE_QA_PATH = (
    PROJECT_ROOT
    / "qa"
    / "qa_summary.csv"
)

REFERENCE_BASE_PATH = (
    PROJECT_ROOT
    / "qa"
    / "effective_bases.csv"
)

REFERENCE_SMALL_BASE_PATH = (
    PROJECT_ROOT
    / "qa"
    / "small_base_qa.csv"
)

REFERENCE_SIG_PATH = (
    PROJECT_ROOT
    / "qa"
    / "significance_test_results.csv"
)


# ============================================================
# SETTINGS
# ============================================================

VALID_RESPONSES = [1, 2, 3]

MIN_TEST_BASE = 100
VERY_SMALL_BASE_LIMIT = 30
SMALL_BASE_LIMIT = 100

NUMERIC_TOLERANCE = 1e-8


MEASURE_LABELS = {
    "a": "Get news",
    "b": "Keep up with politics or political issues",
    "c": "Keep up with sports or pop culture",
    "d": "Entertainment",
    "e": "Keep up with friends and family",
    "f": "Connect with others who share your interests",
    "g": "Look at product reviews or recommendations",
}


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
# LOAD FILES
# ============================================================

df = pd.read_csv(DATA_PATH)
plan = pd.read_csv(PLAN_PATH)

reference_qa = pd.read_csv(
    REFERENCE_QA_PATH
)

reference_bases = pd.read_csv(
    REFERENCE_BASE_PATH
)

reference_small_base = pd.read_csv(
    REFERENCE_SMALL_BASE_PATH
)

reference_sig = pd.read_csv(
    REFERENCE_SIG_PATH
)


print("=" * 72)
print("W144 FINAL QA")
print("=" * 72)


# ============================================================
# HELPERS
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
            f"Unsupported universe expression: "
            f"{expression}"
        )

    variable = match.group(1)
    value = float(match.group(2))

    if variable not in df.columns:
        raise KeyError(
            f"Universe variable not found: "
            f"{variable}"
        )

    return (
        pd.to_numeric(
            df[variable],
            errors="coerce",
        )
        == value
    )


def get_measure_label(variable):

    match = re.search(
        r"WHY_([a-g])_W144$",
        str(variable),
    )

    if not match:
        raise ValueError(
            f"Cannot determine WHY item: "
            f"{variable}"
        )

    return MEASURE_LABELS[
        match.group(1)
    ]


def kish_effective_n(weights):

    weights = pd.to_numeric(
        weights,
        errors="coerce",
    ).dropna()

    if len(weights) == 0:
        return np.nan

    sum_w = weights.sum()
    sum_w2 = (weights ** 2).sum()

    if sum_w2 == 0:
        return np.nan

    return (
        sum_w ** 2
        / sum_w2
    )


def classify_base(n):
    """
    Return presentation value + QA flag.
    """

    n = int(n)

    if n < VERY_SMALL_BASE_LIMIT:
        return (
            f"{n}**",
            "VERY SMALL BASE",
        )

    if n < SMALL_BASE_LIMIT:
        return (
            f"{n}*",
            "SMALL BASE",
        )

    return (
        str(n),
        "OK",
    )


# ============================================================
# REBUILD TABLE-LEVEL QA SUMMARY
# ============================================================

qa_rows = []


for _, row in plan.iterrows():

    table_id = row["table_id"]
    platform = row["platform"]
    variable = row["variable"]
    weight = row["weight"]
    universe_expression = row["universe"]

    universe_mask = parse_universe(
        universe_expression
    )

    eligible = df.loc[
        universe_mask
    ].copy()

    eligible_n = len(eligible)

    valid_mask = (
        eligible[variable].isin(
            VALID_RESPONSES
        )
        &
        eligible[weight].notna()
    )

    valid = eligible.loc[
        valid_mask
    ].copy()

    valid_n = len(valid)

    special_or_invalid_n = (
        eligible_n - valid_n
    )

    weighted_base = (
        valid[weight].sum()
    )

    percentages = []

    if weighted_base > 0:

        for response in VALID_RESPONSES:

            numerator = valid.loc[
                valid[variable] == response,
                weight,
            ].sum()

            percentages.append(
                numerator
                / weighted_base
                * 100
            )

    percentage_sum = (
        sum(percentages)
        if percentages
        else np.nan
    )

    percentage_qa = (
        "PASS"
        if (
            not pd.isna(percentage_sum)
            and abs(
                percentage_sum - 100
            ) <= 0.2
        )
        else "FAIL"
    )

    qa_rows.append({
        "table_id": table_id,
        "platform": platform,
        "variable": variable,
        "weight": weight,
        "eligible_n": eligible_n,
        "valid_n": valid_n,
        "special_or_invalid_n":
            special_or_invalid_n,
        "weighted_base": weighted_base,
        "percentage_qa":
            percentage_qa,
        "measure":
            get_measure_label(variable),
        "universe":
            universe_expression,
    })


qa_summary = pd.DataFrame(
    qa_rows
)


assert len(qa_summary) == 28

assert (
    qa_summary["percentage_qa"]
    == "PASS"
).all()

print(
    "[PASS] Table-level QA rebuilt "
    "(28/28)"
)


# ============================================================
# RECONCILE QA SUMMARY
# ============================================================

qa_keys = [
    "table_id",
    "platform",
    "variable",
    "weight",
    "measure",
    "universe",
]


qa_compare = qa_summary.merge(
    reference_qa,
    on=qa_keys,
    suffixes=("_new", "_ref"),
    validate="one_to_one",
)


assert len(qa_compare) == 28


integer_columns = [
    "eligible_n",
    "valid_n",
    "special_or_invalid_n",
]


for column in integer_columns:

    assert (
        qa_compare[
            f"{column}_new"
        ]
        ==
        qa_compare[
            f"{column}_ref"
        ]
    ).all(), (
        f"{column} differs from "
        f"approved QA results"
    )


weighted_base_difference = (
    qa_compare[
        "weighted_base_new"
    ]
    -
    qa_compare[
        "weighted_base_ref"
    ]
).abs()


assert (
    weighted_base_difference
    < NUMERIC_TOLERANCE
).all(), (
    "Weighted bases differ from "
    "approved QA results"
)


assert (
    qa_compare[
        "percentage_qa_new"
    ]
    ==
    qa_compare[
        "percentage_qa_ref"
    ]
).all()


print(
    "[PASS] QA summary reconciled "
    "with approved results"
)


# ============================================================
# REBUILD EFFECTIVE BASES
# ============================================================

effective_base_rows = []


for _, row in plan.iterrows():

    table_id = row["table_id"]
    platform = row["platform"]
    variable = row["variable"]
    weight = row["weight"]

    universe_mask = parse_universe(
        row["universe"]
    )

    universe_data = df.loc[
        universe_mask
    ].copy()

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    valid = (
        universe_data[variable].isin(
            VALID_RESPONSES
        )
        &
        universe_data[weight].notna()
    )

    total_data = universe_data.loc[
        valid
    ]

    total_n = len(total_data)

    total_neff = kish_effective_n(
        total_data[weight]
    )

    effective_base_rows.append({
        "table_id": table_id,
        "platform": platform,
        "banner": "Total",
        "category": "Total",
        "unweighted_n": total_n,
        "effective_n": total_neff,
        "weighting_deff":
            total_n / total_neff,
    })

    # --------------------------------------------------------
    # BANNERS
    # --------------------------------------------------------

    for banner_var, categories in (
        banner_definitions.items()
    ):

        banner = banner_names[
            banner_var
        ]

        for code, category in (
            categories.items()
        ):

            subset = universe_data.loc[
                universe_data[
                    banner_var
                ] == code
            ]

            valid = (
                subset[variable].isin(
                    VALID_RESPONSES
                )
                &
                subset[weight].notna()
            )

            subset = subset.loc[
                valid
            ]

            n = len(subset)

            neff = kish_effective_n(
                subset[weight]
            )

            deff = (
                n / neff
                if (
                    not pd.isna(neff)
                    and neff > 0
                )
                else np.nan
            )

            effective_base_rows.append({
                "table_id": table_id,
                "platform": platform,
                "banner": banner,
                "category": category,
                "unweighted_n": n,
                "effective_n": neff,
                "weighting_deff": deff,
            })


effective_bases = pd.DataFrame(
    effective_base_rows
)


assert len(effective_bases) == 504

print(
    "[PASS] Effective-base matrix rebuilt "
    "(504/504)"
)


# ============================================================
# EFFECTIVE BASE RECONCILIATION
# ============================================================

base_keys = [
    "table_id",
    "platform",
    "banner",
    "category",
]


base_compare = effective_bases.merge(
    reference_bases,
    on=base_keys,
    suffixes=("_new", "_ref"),
    validate="one_to_one",
)


assert len(base_compare) == 504


assert (
    base_compare[
        "unweighted_n_new"
    ]
    ==
    base_compare[
        "unweighted_n_ref"
    ]
).all()


assert (
    (
        base_compare[
            "effective_n_new"
        ]
        -
        base_compare[
            "effective_n_ref"
        ]
    ).abs()
    < NUMERIC_TOLERANCE
).all()


assert (
    (
        base_compare[
            "weighting_deff_new"
        ]
        -
        base_compare[
            "weighting_deff_ref"
        ]
    ).abs()
    < NUMERIC_TOLERANCE
).all()


print(
    "[PASS] Effective bases reconciled "
    "with approved results"
)


# ============================================================
# REBUILD SMALL-BASE QA
# ============================================================

small_base_rows = []


# Total is intentionally excluded.
banner_only = effective_bases.loc[
    effective_bases["banner"]
    != "Total"
].copy()


assert len(banner_only) == 476


for _, row in banner_only.iterrows():

    displayed_base, flag = (
        classify_base(
            row["unweighted_n"]
        )
    )

    small_base_rows.append({
        "table_id":
            row["table_id"],

        "column":
            (
                f"{row['banner']} | "
                f"{row['category']}"
            ),

        "displayed_base":
            displayed_base,

        "flag":
            flag,
    })


small_base_qa = pd.DataFrame(
    small_base_rows
)


assert len(small_base_qa) == 476

print(
    "[PASS] Small-base QA rebuilt "
    "(476/476)"
)


# ============================================================
# SMALL-BASE COUNTS
# ============================================================

flag_counts = (
    small_base_qa["flag"]
    .value_counts()
    .to_dict()
)


ok_count = flag_counts.get(
    "OK",
    0,
)

small_count = flag_counts.get(
    "SMALL BASE",
    0,
)

very_small_count = flag_counts.get(
    "VERY SMALL BASE",
    0,
)


assert ok_count == 448, (
    f"Expected 448 OK cells; "
    f"found {ok_count}"
)

assert small_count == 21, (
    f"Expected 21 SMALL BASE cells; "
    f"found {small_count}"
)

assert very_small_count == 7, (
    f"Expected 7 VERY SMALL BASE cells; "
    f"found {very_small_count}"
)


print(
    "[PASS] Small-base distribution: "
    "448 OK | 21 SMALL | 7 VERY SMALL"
)


# ============================================================
# RECONCILE SMALL-BASE QA
# ============================================================

small_compare = (
    small_base_qa.merge(
        reference_small_base,
        on=[
            "table_id",
            "column",
        ],
        suffixes=(
            "_new",
            "_ref",
        ),
        validate="one_to_one",
    )
)


assert len(small_compare) == 476


assert (
    small_compare[
        "displayed_base_new"
    ].astype(str)
    ==
    small_compare[
        "displayed_base_ref"
    ].astype(str)
).all(), (
    "Displayed small-base values "
    "differ from approved output"
)


assert (
    small_compare["flag_new"]
    ==
    small_compare["flag_ref"]
).all(), (
    "Small-base flags differ "
    "from approved output"
)


print(
    "[PASS] Small-base flags reconciled "
    "with approved results"
)


# ============================================================
# VERIFY LOCATION OF LOW-BASE CELLS
# ============================================================

low_base_cells = (
    banner_only.loc[
        banner_only[
            "unweighted_n"
        ] < MIN_TEST_BASE
    ]
    .copy()
)


assert len(low_base_cells) == 28, (
    f"Expected 28 low-base cells; "
    f"found {len(low_base_cells)}"
)


assert (
    low_base_cells["banner"]
    == "Gender"
).all(), (
    "Unexpected banner contains "
    "N < 100 cells"
)


assert (
    low_base_cells["category"]
    == "In some other way"
).all(), (
    "Unexpected category contains "
    "N < 100 cells"
)


print(
    "[PASS] All 28 N < 100 cells are "
    "'Gender | In some other way'"
)


# ============================================================
# PLATFORM LOW-BASE CHECK
# ============================================================

low_base_platform = (
    low_base_cells
    .groupby("platform")
    .agg(
        tables=(
            "table_id",
            "nunique",
        ),
        min_n=(
            "unweighted_n",
            "min",
        ),
        max_n=(
            "unweighted_n",
            "max",
        ),
    )
)


expected_low_base_ranges = {
    "Facebook": (7, 35, 36),
    "Instagram": (7, 44, 44),
    "X": (7, 28, 29),
    "TikTok": (7, 32, 32),
}


for platform, (
    expected_tables,
    expected_min,
    expected_max,
) in expected_low_base_ranges.items():

    actual = low_base_platform.loc[
        platform
    ]

    assert (
        actual["tables"]
        == expected_tables
    )

    assert (
        actual["min_n"]
        == expected_min
    )

    assert (
        actual["max_n"]
        == expected_max
    )


print(
    "[PASS] Platform-specific low-base "
    "ranges validated"
)


# ============================================================
# SIGNIFICANCE LOW-BASE QA
# ============================================================

assert len(reference_sig) == 1596


sig_low_base = reference_sig.loc[
    (reference_sig["n_1"] < MIN_TEST_BASE)
    |
    (reference_sig["n_2"] < MIN_TEST_BASE)
]


assert sig_low_base.empty, (
    "Low-base categories were used "
    "in significance testing"
)


print(
    "[PASS] Zero significance tests "
    "involve N < 100 categories"
)


# ============================================================
# FINAL CROSS-CHECKS
# ============================================================

assert qa_summary["table_id"].nunique() == 28
assert effective_bases["table_id"].nunique() == 28
assert small_base_qa["table_id"].nunique() == 28
assert reference_sig["table_id"].nunique() == 28

assert qa_summary["platform"].nunique() == 4
assert effective_bases["platform"].nunique() == 4

assert qa_summary["variable"].nunique() == 28
assert qa_summary["measure"].nunique() == 7


print(
    "[PASS] Final project coverage "
    "validated"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "-" * 72)
print("FINAL QA SUMMARY")
print("-" * 72)

print(
    f"Tables:                       "
    f"{len(qa_summary)}"
)

print(
    f"Percentage-QA PASS:           "
    f"{(qa_summary['percentage_qa'] == 'PASS').sum()}/28"
)

print(
    f"Effective-base records:       "
    f"{len(effective_bases)}"
)

print(
    f"Banner cells reviewed:        "
    f"{len(small_base_qa)}"
)

print(
    f"Adequate bases (N >= 100):    "
    f"{ok_count}"
)

print(
    f"Small bases (30 <= N < 100):  "
    f"{small_count}"
)

print(
    f"Very small bases (N < 30):    "
    f"{very_small_count}"
)

print(
    f"Low-base significance tests:  "
    f"{len(sig_low_base)}"
)

print(
    f"Significance tests reviewed:  "
    f"{len(reference_sig):,}"
)


print("\nLow-base cells by platform:")

print(
    low_base_platform
    .to_string()
)


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 72)
print("FINAL QA VALIDATION PASSED")
print("=" * 72)