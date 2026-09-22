"""
03_tabulation_engine.py

Builds the 28 weighted cross-tabulations used in the
W144 Social Media Platform Usage & User Motivations study.

The script:
1. Reads the raw W144 survey data.
2. Reads the approved tabulation plan.
3. Applies the correct analytical universe and platform weight.
4. Calculates unweighted bases and weighted column percentages.
5. Produces Total + demographic banner columns.
6. Validates percentage totals and table structure.
7. Exports T01-T28 to output/tables/.
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "output"
    / "tables"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

VALID_RESPONSES = [1, 2, 3]

RESPONSE_LABELS = {
    1: "Major reason",
    2: "Minor reason",
    3: "Not a reason",
}

PERCENT_TOLERANCE = 0.2


# ============================================================
# BANNER DEFINITIONS
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

print("=" * 70)
print("W144 TABULATION ENGINE")
print("=" * 70)

print(f"\nRaw data: {df.shape[0]:,} rows x {df.shape[1]:,} columns")
print(f"Tabulation plan: {len(plan)} tables")


# ============================================================
# BASIC PLAN VALIDATION
# ============================================================

assert len(plan) == 28, (
    f"Expected 28 tables; found {len(plan)}"
)

assert plan["table_id"].nunique() == 28, (
    "Duplicate table IDs detected"
)

assert plan["variable"].nunique() == 28, (
    "Duplicate analytical variables detected"
)

print("\n[PASS] Tabulation plan structure")


# ============================================================
# UNIVERSE PARSER
# ============================================================

def parse_universe(expression):
    """
    Parse simple universe expressions such as:

        DOV_ASKFB_W144 == 1
        SMUSE_c_W144 == 1

    Returns a Boolean mask.
    """

    pattern = (
        r"^\s*([A-Za-z0-9_]+)\s*==\s*"
        r"(-?\d+(?:\.\d+)?)\s*$"
    )

    match = re.match(pattern, str(expression))

    if not match:
        raise ValueError(
            f"Unsupported universe expression: {expression}"
        )

    variable = match.group(1)
    value = float(match.group(2))

    if variable not in df.columns:
        raise KeyError(
            f"Universe variable not found: {variable}"
        )

    return (
        pd.to_numeric(df[variable], errors="coerce")
        == value
    )


# ============================================================
# WEIGHTED PERCENTAGE
# ============================================================

def weighted_percentage(data, outcome, response, weight):
    """
    Weighted percentage among substantive responses 1/2/3.
    """

    valid = (
        data[outcome].isin(VALID_RESPONSES)
        & data[weight].notna()
    )

    denominator = data.loc[
        valid,
        weight
    ].sum()

    numerator = data.loc[
        valid & (data[outcome] == response),
        weight
    ].sum()

    if denominator == 0:
        return np.nan

    return numerator / denominator * 100


# ============================================================
# COLUMN CALCULATION
# ============================================================

def calculate_column(
    data,
    outcome,
    weight,
    banner_variable=None,
    banner_code=None,
):
    """
    Calculate one analytical column.

    Base is the unweighted number of respondents with a
    substantive WHY response (1/2/3) and a nonmissing weight.
    """

    subset = data

    if banner_variable is not None:
        subset = subset.loc[
            subset[banner_variable] == banner_code
        ]

    valid = (
        subset[outcome].isin(VALID_RESPONSES)
        & subset[weight].notna()
    )

    base = int(valid.sum())

    percentages = {}

    for response in VALID_RESPONSES:
        percentages[response] = weighted_percentage(
            subset,
            outcome,
            response,
            weight,
        )

    return {
        "base": base,
        "percentages": percentages,
    }


# ============================================================
# GENERATE ONE TABLE
# ============================================================

def generate_crosstab(plan_row):
    """
    Generate Total + five demographic banners for one WHY outcome.
    """

    table_id = plan_row["table_id"]
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

    universe_mask = parse_universe(
        plan_row["universe"]
    )

    universe_data = df.loc[
        universe_mask
    ].copy()

    columns = []

    # TOTAL
    result = calculate_column(
        universe_data,
        outcome,
        weight,
    )

    columns.append({
        "banner": "Total",
        "category": "Total",
        "base": result["base"],
        **{
            RESPONSE_LABELS[r]:
                result["percentages"][r]
            for r in VALID_RESPONSES
        },
    })

    # BANNERS
    banner_fields = [
        "banner_1",
        "banner_2",
        "banner_3",
        "banner_4",
        "banner_5",
    ]

    for banner_field in banner_fields:

        banner_var = plan_row[banner_field]

        if pd.isna(banner_var):
            continue

        banner_var = str(banner_var).strip()

        if banner_var not in banner_definitions:
            raise KeyError(
                f"{table_id}: no definition for {banner_var}"
            )

        for code, label in (
            banner_definitions[banner_var].items()
        ):

            result = calculate_column(
                universe_data,
                outcome,
                weight,
                banner_variable=banner_var,
                banner_code=code,
            )

            columns.append({
                "banner": banner_names[banner_var],
                "category": label,
                "base": result["base"],
                **{
                    RESPONSE_LABELS[r]:
                        result["percentages"][r]
                    for r in VALID_RESPONSES
                },
            })

    return pd.DataFrame(columns)


# ============================================================
# GENERATE ALL 28 TABLES
# ============================================================

tab_book = {}

for _, row in plan.iterrows():

    table_id = row["table_id"]

    tab_book[table_id] = generate_crosstab(row)

assert len(tab_book) == 28

print("[PASS] 28 cross-tabs generated")


# ============================================================
# PERCENTAGE QA
# ============================================================

percentage_checks = []

for table_id, table in tab_book.items():

    for _, row in table.iterrows():

        percentages = [
            row["Major reason"],
            row["Minor reason"],
            row["Not a reason"],
        ]

        if any(pd.isna(x) for x in percentages):
            total = np.nan
            passed = False

        else:
            total = sum(percentages)

            passed = (
                abs(total - 100)
                <= PERCENT_TOLERANCE
            )

        percentage_checks.append({
            "table_id": table_id,
            "banner": row["banner"],
            "category": row["category"],
            "base": row["base"],
            "percentage_sum": total,
            "pass": passed,
        })


percentage_qa = pd.DataFrame(
    percentage_checks
)

failed_percentage_checks = percentage_qa.loc[
    ~percentage_qa["pass"]
]

assert failed_percentage_checks.empty, (
    "Percentage QA failures detected:\n"
    f"{failed_percentage_checks}"
)

print(
    f"[PASS] Percentage validation "
    f"({len(percentage_qa)}/{len(percentage_qa)})"
)


# ============================================================
# EXPECTED COLUMN COUNT
# ============================================================

# Total:     1
# Age:       4
# Gender:    3
# Education: 3
# Region:    4
# Income:    3
#
# Total = 18 analytical columns per table.

expected_columns_per_table = (
    1
    + 4
    + 3
    + 3
    + 4
    + 3
)

assert expected_columns_per_table == 18

for table_id, table in tab_book.items():

    assert len(table) == expected_columns_per_table, (
        f"{table_id}: expected 18 columns, "
        f"found {len(table)}"
    )

print("[PASS] Banner structure (18 columns per table)")


# ============================================================
# KNOWN BASE RECONCILIATION
# ============================================================

# T01 was independently validated during development.
# Its total substantive-response base should be 7,135.

assert tab_book["T01"].iloc[0]["base"] == 7135, (
    "T01 total base does not match approved result"
)

print("[PASS] T01 approved base reconciled")


# ============================================================
# EXPORT TABLES
# ============================================================

def export_table(table_id, table):
    """
    Convert the analytical row-oriented table into the
    presentation-oriented CSV structure used by the tab book.

    Output rows:
        Unweighted Base
        Major reason
        Minor reason
        Not a reason

    Output columns:
        Total
        Age | ...
        Gender | ...
        Education | ...
        Region | ...
        Income | ...
    """

    output = pd.DataFrame()

    for _, column in table.iterrows():

        if column["banner"] == "Total":
            column_name = "Total"
        else:
            column_name = (
                f"{column['banner']} | "
                f"{column['category']}"
            )

        output[column_name] = [
            int(column["base"]),
            column["Major reason"],
            column["Minor reason"],
            column["Not a reason"],
        ]

    output.index = [
        "Unweighted Base",
        "Major reason",
        "Minor reason",
        "Not a reason",
    ]

    output.index.name = None

    return output


exported_tables = {}

for table_id, table in tab_book.items():

    export_df = export_table(
        table_id,
        table,
    )

    output_path = (
        OUTPUT_DIR
        / f"{table_id}.csv"
    )

    export_df.to_csv(
        output_path,
        index=True,
        float_format="%.6f",
    )

    exported_tables[table_id] = output_path


assert len(exported_tables) == 28

missing_exports = [
    table_id
    for table_id, path in exported_tables.items()
    if not path.exists()
]

assert not missing_exports, (
    f"Missing exported tables: {missing_exports}"
)

print(
    f"[PASS] Exported 28 tables to "
    f"{OUTPUT_DIR.relative_to(PROJECT_ROOT)}"
)


# ============================================================
# EXPORT READABILITY QA
# ============================================================

export_qa = []

for table_id, path in exported_tables.items():

    exported = pd.read_csv(
        path,
        index_col=0,
    )

    export_qa.append({
        "table_id": table_id,
        "rows": len(exported),
        "columns": len(exported.columns),
        "nonempty": not exported.empty,
        "correct_rows": len(exported) == 4,
        "correct_columns": len(exported.columns) == 18,
    })


export_qa = pd.DataFrame(export_qa)

assert export_qa["nonempty"].all()
assert export_qa["correct_rows"].all()
assert export_qa["correct_columns"].all()

print(
    "[PASS] Export validation "
    "(28 files x 4 rows x 18 analytical columns)"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "-" * 70)
print("TABULATION SUMMARY")
print("-" * 70)

print(f"Tables generated:       {len(tab_book)}")
print("Columns per table:      18")
print(f"Percentage QA checks:   {len(percentage_qa)}")
print(
    f"Failed percentage QA:   "
    f"{len(failed_percentage_checks)}"
)
print(f"Tables exported:        {len(exported_tables)}")

print("\nT01 analytical preview:")
print(
    tab_book["T01"]
    .round(1)
    .to_string(index=False)
)

print("\nT01 export preview:")
print(
    pd.read_csv(
        exported_tables["T01"],
        index_col=0,
    )
    .round(1)
    .to_string()
)


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 70)
print("TABULATION ENGINE PASSED AND TABLES EXPORTED")
print("=" * 70)