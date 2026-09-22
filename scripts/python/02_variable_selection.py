"""
02_variable_selection.py

Defines and validates the analytical variables used in the
Pew Research Center American Trends Panel Wave 144
survey tabulation study.

Portfolio project:
Social Media Platform Usage & User Motivations
"""

from pathlib import Path
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

REFERENCE_PATH = (
    PROJECT_ROOT
    / "tabulation"
    / "variable_selection_matrix.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)


# ============================================================
# ANALYTICAL OUTCOMES
# ============================================================

# Seven WHY items per platform:
# a = Get news
# b = Politics or political issues
# c = Sports or pop culture
# d = Entertainment
# e = Friends and family
# f = Shared interests
# g = Product reviews or recommendations

why_variables = {
    "Facebook": [
        f"FBWHY_{letter}_W144"
        for letter in "abcdefg"
    ],
    "Instagram": [
        f"IGWHY_{letter}_W144"
        for letter in "abcdefg"
    ],
    "X": [
        f"XTWHY_{letter}_W144"
        for letter in "abcdefg"
    ],
    "TikTok": [
        f"TTWHY_{letter}_W144"
        for letter in "abcdefg"
    ],
}


# ============================================================
# PRIMARY BANNERS
# ============================================================

banner_variables = [
    "F_AGECAT",
    "F_GENDER",
    "F_EDUCCAT",
    "F_CREGION",
    "F_INC_TIER2",
]


# ============================================================
# PLATFORM WEIGHTS
# ============================================================

weight_variables = {
    "Facebook": "WEIGHT_W144_FB",
    "Instagram": "WEIGHT_W144_IG",
    "X": "WEIGHT_W144_XT",
    "TikTok": "WEIGHT_W144_TT",
}


# ============================================================
# ANALYTICAL UNIVERSES
# ============================================================

universe_variables = {
    "Facebook": "DOV_ASKFB_W144",
    "Instagram": "DOV_ASKIG_W144",
    "X": "SMUSE_c_W144",
    "TikTok": "SMUSE_i_W144",
}


# ============================================================
# START VALIDATION
# ============================================================

print("=" * 60)
print("VARIABLE SELECTION VALIDATION")
print("=" * 60)


# ============================================================
# ANALYTICAL VARIABLE PRESENCE
# ============================================================

why_flat = [
    variable
    for variables in why_variables.values()
    for variable in variables
]

analysis_variables = (
    why_flat
    + banner_variables
    + list(weight_variables.values())
    + list(universe_variables.values())
)

missing_variables = [
    variable
    for variable in analysis_variables
    if variable not in df.columns
]

assert not missing_variables, (
    "Missing analytical variables: "
    f"{missing_variables}"
)

print("\n[PASS] All analytical variables present")


# ============================================================
# WHY BATTERY STRUCTURE
# ============================================================

assert len(why_flat) == 28, (
    f"Expected 28 WHY variables; found {len(why_flat)}"
)

assert len(set(why_flat)) == 28, (
    "Duplicate WHY variables detected"
)

for platform, variables in why_variables.items():

    assert len(variables) == 7, (
        f"{platform}: expected 7 WHY variables; "
        f"found {len(variables)}"
    )

print("[PASS] 28 WHY variables identified")


# ============================================================
# WHY RESPONSE CODE VALIDATION
# ============================================================

# Substantive response codes:
# 1 = Major reason
# 2 = Minor reason
# 3 = Not a reason
#
# Code 99 is retained as a special/non-substantive code
# for QA purposes and excluded from analytical percentage bases.

allowed_codes = {1, 2, 3, 99}

unexpected_codes = {}

for variable in why_flat:

    observed = set(
        pd.to_numeric(
            df[variable],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
    )

    invalid_codes = observed - allowed_codes

    if invalid_codes:
        unexpected_codes[variable] = sorted(
            invalid_codes
        )

assert not unexpected_codes, (
    "Unexpected WHY response codes detected: "
    f"{unexpected_codes}"
)

print("[PASS] WHY response codes valid")


# ============================================================
# WHY ROUTING QA
# ============================================================

universe_masks = {
    "Facebook": df["DOV_ASKFB_W144"] == 1,
    "Instagram": df["DOV_ASKIG_W144"] == 1,
    "X": df["SMUSE_c_W144"] == 1,
    "TikTok": df["SMUSE_i_W144"] == 1,
}

routing_qa_rows = []

for platform, variables in why_variables.items():
    universe = universe_masks[platform]

    for variable in variables:
        values = pd.to_numeric(
            df[variable],
            errors="coerce",
        )

        observed = df[variable].notna()
        nonnumeric = observed & values.isna()
        unexpected = (
            observed
            & ~values.isin(allowed_codes)
        )
        response_present = values.isin(allowed_codes)

        routing_qa_rows.append({
            "platform": platform,
            "variable": variable,
            "universe_n": int(universe.sum()),
            "substantive_inside_n": int(
                (universe & values.isin({1, 2, 3})).sum()
            ),
            "special_99_inside_n": int(
                (universe & values.eq(99)).sum()
            ),
            "missing_inside_n": int(
                (universe & ~observed).sum()
            ),
            "responses_outside_n": int(
                (~universe & response_present).sum()
            ),
            "unexpected_code_n": int(unexpected.sum()),
            "nonnumeric_response_n": int(nonnumeric.sum()),
        })

routing_qa = pd.DataFrame(routing_qa_rows)

assert len(routing_qa) == 28
assert routing_qa["responses_outside_n"].eq(0).all(), (
    "WHY responses detected outside analytical universes:\n"
    f"{routing_qa.loc[routing_qa['responses_outside_n'] > 0]}"
)
assert routing_qa["unexpected_code_n"].eq(0).all(), (
    "Unexpected WHY response codes detected:\n"
    f"{routing_qa.loc[routing_qa['unexpected_code_n'] > 0]}"
)
assert routing_qa["nonnumeric_response_n"].eq(0).all(), (
    "Nonnumeric WHY responses detected:\n"
    f"{routing_qa.loc[routing_qa['nonnumeric_response_n'] > 0]}"
)

print(
    "[PASS] WHY routing QA "
    "(28 variables; zero responses outside universe)"
)
print(
    "       Missing responses inside universes: "
    f"{routing_qa['missing_inside_n'].sum():,}"
)


# ============================================================
# WEIGHT INTEGRITY QA
# ============================================================

weight_qa_rows = []

for platform, weight in weight_variables.items():
    universe = universe_masks[platform]
    raw_weight = df[weight]
    numeric_weight = pd.to_numeric(
        raw_weight,
        errors="coerce",
    )

    nonnumeric = raw_weight.notna() & numeric_weight.isna()
    nonfinite = (
        numeric_weight.notna()
        & ~np.isfinite(numeric_weight)
    )
    nonpositive = (
        numeric_weight.notna()
        & np.isfinite(numeric_weight)
        & numeric_weight.le(0)
    )
    analytical = (
        universe
        & df[why_variables[platform]].isin({1, 2, 3}).any(axis=1)
    )

    weight_qa_rows.append({
        "platform": platform,
        "weight": weight,
        "universe_n": int(universe.sum()),
        "analytical_respondent_n": int(analytical.sum()),
        "missing_in_universe_n": int(
            (universe & raw_weight.isna()).sum()
        ),
        "nonnumeric_n": int(nonnumeric.sum()),
        "nonfinite_analytical_n": int(
            (analytical & nonfinite).sum()
        ),
        "nonpositive_analytical_n": int(
            (analytical & nonpositive).sum()
        ),
        "missing_analytical_n": int(
            (analytical & raw_weight.isna()).sum()
        ),
    })

weight_qa = pd.DataFrame(weight_qa_rows)

assert len(weight_qa) == 4
invalid_weight_columns = [
    "nonnumeric_n",
    "nonfinite_analytical_n",
    "nonpositive_analytical_n",
    "missing_analytical_n",
]
invalid_weight_rows = weight_qa.loc[
    weight_qa[invalid_weight_columns].sum(axis=1) > 0
]
assert invalid_weight_rows.empty, (
    "Invalid analytical survey weights detected:\n"
    f"{invalid_weight_rows}"
)

print("[PASS] Platform weight integrity QA")
for _, weight_row in weight_qa.iterrows():
    print(
        f"       {weight_row['platform']}: "
        f"missing in universe="
        f"{weight_row['missing_in_universe_n']}"
    )


# ============================================================
# SAVED VARIABLE SELECTION MATRIX
# ============================================================

assert REFERENCE_PATH.exists(), (
    f"Reference selection matrix not found: "
    f"{REFERENCE_PATH}"
)

reference = pd.read_csv(REFERENCE_PATH)

required_reference_columns = {
    "variable",
    "final_status",
}

missing_reference_columns = (
    required_reference_columns
    - set(reference.columns)
)

assert not missing_reference_columns, (
    "Missing columns in variable selection matrix: "
    f"{sorted(missing_reference_columns)}"
)


# Normalize variable names/status for comparison.

reference["variable"] = (
    reference["variable"]
    .astype(str)
    .str.strip()
)

reference["final_status"] = (
    reference["final_status"]
    .astype(str)
    .str.strip()
    .str.upper()
)

included_variables = set(
    reference.loc[
        reference["final_status"] == "INCLUDE",
        "variable",
    ]
)


# ============================================================
# RECONCILE WHY VARIABLES
# ============================================================

missing_why_from_reference = sorted(
    set(why_flat)
    - included_variables
)

assert not missing_why_from_reference, (
    "WHY variables missing from saved selection matrix: "
    f"{missing_why_from_reference}"
)

print(
    "[PASS] Saved variable selection matrix reconciled"
)


# ============================================================
# RECONCILE PRIMARY BANNERS
# ============================================================

missing_banners = sorted(
    set(banner_variables)
    - included_variables
)

assert not missing_banners, (
    "Primary banners missing from selection matrix: "
    f"{missing_banners}"
)

print(
    "[PASS] Five primary banner variables reconciled"
)


# ============================================================
# VERIFY PLATFORM CONFIGURATION
# ============================================================

expected_platforms = {
    "Facebook",
    "Instagram",
    "X",
    "TikTok",
}

assert set(why_variables) == expected_platforms
assert set(weight_variables) == expected_platforms
assert set(universe_variables) == expected_platforms

print("[PASS] Platform configuration reconciled")


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print("\nSelected analytical outcomes:")

for platform, variables in why_variables.items():
    print(f"  {platform}: {len(variables)}")

print(
    f"\nPrimary banners: "
    f"{len(banner_variables)}"
)

print(
    f"WHY outcomes: "
    f"{len(why_flat)}"
)


# ============================================================
# PLATFORM CONFIGURATION SUMMARY
# ============================================================

print("\nPlatform configuration:")

for platform in why_variables:

    print(
        f"  {platform}: "
        f"{len(why_variables[platform])} outcomes | "
        f"universe={universe_variables[platform]} | "
        f"weight={weight_variables[platform]}"
    )


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("VARIABLE SELECTION VALIDATION PASSED")
print("=" * 60)
