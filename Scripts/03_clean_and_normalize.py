from pathlib import Path
import pandas as pd


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_CSV = PROJECT_ROOT / "data" / "validated_game_scores.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "normalized_game_scores.csv"


# ============================================================
# Load validated data
# ============================================================

print("Loading validated game scores...")

df = pd.read_csv(INPUT_CSV)

print(f"Rows loaded: {len(df)}")


# ============================================================
# Check required columns
# ============================================================

required_columns = [
    "max_score",
    "raw_best_score",
    "raw_average_score"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# Normalize scores to 0-1
# ============================================================

df["normalized_best_score"] = (
    df["raw_best_score"] / df["max_score"]
)

df["normalized_average_score"] = (
    df["raw_average_score"] / df["max_score"]
)


# ============================================================
# Convert to percentage (0-100)
# ============================================================

df["best_score_percent"] = (
    df["normalized_best_score"] * 100
)

df["average_score_percent"] = (
    df["normalized_average_score"] * 100
)


# ============================================================
# Round values
# ============================================================

df["normalized_best_score"] = (
    df["normalized_best_score"].round(4)
)

df["normalized_average_score"] = (
    df["normalized_average_score"].round(4)
)

df["best_score_percent"] = (
    df["best_score_percent"].round(2)
)

df["average_score_percent"] = (
    df["average_score_percent"].round(2)
)


# ============================================================
# Final range check
# ============================================================

normalized_columns = [
    "normalized_best_score",
    "normalized_average_score"
]

percentage_columns = [
    "best_score_percent",
    "average_score_percent"
]

print("\n--- Normalization Check ---")

for col in normalized_columns:
    print(
        f"{col}: "
        f"min={df[col].min()}, "
        f"max={df[col].max()}"
    )

for col in percentage_columns:
    print(
        f"{col}: "
        f"min={df[col].min()}, "
        f"max={df[col].max()}"
    )


# ============================================================
# Save normalized data
# ============================================================

df.to_csv(
    OUTPUT_CSV,
    index=False
)

print("\nNormalization completed.")
print(f"Saved to: {OUTPUT_CSV}")