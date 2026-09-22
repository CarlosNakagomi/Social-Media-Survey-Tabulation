"""
01_data_validation.py

Initial data validation for the Pew Research Center
American Trends Panel Wave 144 survey.

Portfolio project: Survey Tabulation Study
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "ATP_W144.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("W144 DATA VALIDATION")
print("=" * 60)

print(f"\nDataset: {DATA_PATH.name}")
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]:,}")


# ============================================================
# STRUCTURE CHECK
# ============================================================

EXPECTED_ROWS = 10454
EXPECTED_COLUMNS = 195

assert df.shape == (EXPECTED_ROWS, EXPECTED_COLUMNS), (
    f"Unexpected dataset shape: {df.shape}"
)

print("\n[PASS] Dataset dimensions")


# ============================================================
# REQUIRED VARIABLES
# ============================================================

required_variables = [
    # ID
    "QKEY",

    # Platform usage
    "SMUSE_a_W144",
    "SMUSE_c_W144",
    "SMUSE_d_W144",
    "SMUSE_i_W144",

    # Frequency
    "SMUSE2_a_W144",
    "SMUSE2_c_W144",
    "SMUSE2_d_W144",
    "SMUSE2_i_W144",

    # News use
    "SOCIALNEWS2_a_W144",
    "SOCIALNEWS2_c_W144",
    "SOCIALNEWS2_d_W144",
    "SOCIALNEWS2_i_W144",

    # Routing
    "DOV_USE4_W144",
    "DOV_ASKFB_W144",
    "DOV_ASKIG_W144",
    "XRAND_FB_IG_W144",

    # Banners
    "F_AGECAT",
    "F_GENDER",
    "F_EDUCCAT",
    "F_CREGION",
    "F_INC_TIER2",

    # Weights
    "WEIGHT_W144",
    "WEIGHT_W144_FB",
    "WEIGHT_W144_IG",
    "WEIGHT_W144_XT",
    "WEIGHT_W144_TT",
]

missing_required = [
    var for var in required_variables
    if var not in df.columns
]

assert not missing_required, (
    f"Missing required variables: {missing_required}"
)

print("[PASS] Required variables present")


# ============================================================
# VARIABLE INVENTORY
# ============================================================

variable_inventory = pd.DataFrame({
    "variable": df.columns,
    "dtype": df.dtypes.astype(str).values,
    "n_total": len(df),
    "n_nonmissing": df.notna().sum().values,
    "n_missing": df.isna().sum().values,
    "missing_pct": (df.isna().mean().values * 100).round(2),
    "n_unique": df.nunique(dropna=True).values,
})

print("[PASS] Variable inventory created")


# ============================================================
# PLATFORM ROUTING QA
# ============================================================

platforms = {
    "Facebook": (
        "SMUSE_a_W144",
        "SMUSE2_a_W144",
        "SOCIALNEWS2_a_W144",
    ),
    "X": (
        "SMUSE_c_W144",
        "SMUSE2_c_W144",
        "SOCIALNEWS2_c_W144",
    ),
    "Instagram": (
        "SMUSE_d_W144",
        "SMUSE2_d_W144",
        "SOCIALNEWS2_d_W144",
    ),
    "TikTok": (
        "SMUSE_i_W144",
        "SMUSE2_i_W144",
        "SOCIALNEWS2_i_W144",
    ),
}

routing_results = []

for platform, (use_var, freq_var, news_var) in platforms.items():

    users = df[use_var] == 1
    nonusers = df[use_var] == 2

    result = {
        "platform": platform,
        "users": int(users.sum()),
        "users_missing_frequency":
            int((users & df[freq_var].isna()).sum()),
        "nonusers_with_frequency":
            int((nonusers & df[freq_var].notna()).sum()),
        "users_missing_socialnews":
            int((users & df[news_var].isna()).sum()),
        "nonusers_with_socialnews":
            int((nonusers & df[news_var].notna()).sum()),
    }

    routing_results.append(result)

routing_qa = pd.DataFrame(routing_results)

routing_failures = (
    routing_qa[
        [
            "users_missing_frequency",
            "nonusers_with_frequency",
            "users_missing_socialnews",
            "nonusers_with_socialnews",
        ]
    ]
    .to_numpy()
    .sum()
)

assert routing_failures == 0

print("[PASS] Platform routing QA")


# ============================================================
# DOV ROUTING QA
# ============================================================

smuse_vars = [
    "SMUSE_a_W144",
    "SMUSE_c_W144",
    "SMUSE_d_W144",
    "SMUSE_i_W144",
]

valid_smuse = df[smuse_vars].isin([1, 2]).all(axis=1)

uses_any_platform = (
    df[smuse_vars].eq(1).any(axis=1)
)

dov_universe = valid_smuse & uses_any_platform


expected_use4 = (
    df[smuse_vars].eq(1).all(axis=1)
).astype(int)

expected_askfb = (
    (
        (df["SMUSE_a_W144"] == 1)
        & (expected_use4 == 0)
    )
    |
    (
        (expected_use4 == 1)
        & (df["XRAND_FB_IG_W144"] == 1)
    )
).astype(int)

expected_askig = (
    (
        (df["SMUSE_d_W144"] == 1)
        & (expected_use4 == 0)
    )
    |
    (
        (expected_use4 == 1)
        & (df["XRAND_FB_IG_W144"] == 2)
    )
).astype(int)


dov_checks = {
    "DOV_USE4_W144":
        expected_use4,

    "DOV_ASKFB_W144":
        expected_askfb,

    "DOV_ASKIG_W144":
        expected_askig,
}


for variable, expected in dov_checks.items():

    actual = df.loc[dov_universe, variable]
    expected = expected.loc[dov_universe]

    mismatches = int(
        (actual != expected).sum()
    )

    assert mismatches == 0, (
        f"{variable}: {mismatches} routing mismatches"
    )

print("[PASS] DOV routing QA")


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("ALL INITIAL DATA VALIDATION CHECKS PASSED")
print("=" * 60)
