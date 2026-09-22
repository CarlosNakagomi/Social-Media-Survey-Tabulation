"""
02_variable_selection.py

Defines and validates the analytical variables used in the
Pew Research Center American Trends Panel Wave 144
survey tabulation study.

Portfolio project:
Social Media Platform Usage & User Motivations
"""

from pathlib import Path
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