from pathlib import Path
import pandas as pd


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_CSV = PROJECT_ROOT / "data" / "game_scores.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "validated_game_scores.csv"


# ============================================================
# Load data
# ============================================================

print("Loading game scores...")

df = pd.read_csv(INPUT_CSV)

print(f"Rows loaded: {len(df)}")


# ============================================================
# Required columns
# ============================================================

required_columns = [
    "player_id",
    "game_id",
    "game_title",
    "game_type",
    "cognitive_skills",
    "max_score",
    "raw_best_score",
    "raw_average_score",
    "play_count"
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
# Convert numeric columns
# ============================================================

numeric_columns = [
    "game_id",
    "max_score",
    "raw_best_score",
    "raw_average_score",
    "play_count"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# ============================================================
# Validation statistics
# ============================================================

print("\n--- Validation Report ---")

# Missing values
print("\nMissing values:")
print(df[required_columns].isnull().sum())


# Duplicate player-game combinations
duplicates = df.duplicated(
    subset=["player_id", "game_id"],
    keep=False
)

print(
    f"\nDuplicate player-game records: "
    f"{duplicates.sum()}"
)


# Invalid max scores
invalid_max = df["max_score"] <= 0

print(
    f"Invalid max_score records: "
    f"{invalid_max.sum()}"
)


# Invalid play counts
invalid_play_count = df["play_count"] <= 0

print(
    f"Invalid play_count records: "
    f"{invalid_play_count.sum()}"
)


# ============================================================
# Score correction
# ============================================================

print("\nCorrecting scores...")

# ------------------------------------------------------------
# Negative scores -> 0
# ------------------------------------------------------------

negative_best = df["raw_best_score"] < 0
negative_average = df["raw_average_score"] < 0

print(
    f"Negative best scores corrected: "
    f"{negative_best.sum()}"
)

print(
    f"Negative average scores corrected: "
    f"{negative_average.sum()}"
)

df.loc[negative_best, "raw_best_score"] = 0
df.loc[negative_average, "raw_average_score"] = 0


# ------------------------------------------------------------
# Scores above maximum -> maximum score
# ------------------------------------------------------------

best_above_max = (
    df["raw_best_score"] > df["max_score"]
)

average_above_max = (
    df["raw_average_score"] > df["max_score"]
)

print(
    f"Best scores above max corrected: "
    f"{best_above_max.sum()}"
)

print(
    f"Average scores above max corrected: "
    f"{average_above_max.sum()}"
)

df.loc[best_above_max, "raw_best_score"] = (
    df.loc[best_above_max, "max_score"]
)

df.loc[average_above_max, "raw_average_score"] = (
    df.loc[average_above_max, "max_score"]
)


# ============================================================
# Best score should not be lower than average score
# ============================================================

best_lower_than_average = (
    df["raw_best_score"] < df["raw_average_score"]
)

print(
    f"\nBest score < average score records: "
    f"{best_lower_than_average.sum()}"
)

if best_lower_than_average.sum() > 0:
    print(
        "Warning: These records were NOT automatically changed."
    )
    print(
        "They should be investigated because bestScore "
        "should normally be >= averageScore."
    )


# ============================================================
# Final score range check
# ============================================================

invalid_best_after = (
    (df["raw_best_score"] < 0) |
    (df["raw_best_score"] > df["max_score"])
)

invalid_average_after = (
    (df["raw_average_score"] < 0) |
    (df["raw_average_score"] > df["max_score"])
)

print(
    f"\nInvalid best scores after correction: "
    f"{invalid_best_after.sum()}"
)

print(
    f"Invalid average scores after correction: "
    f"{invalid_average_after.sum()}"
)


# ============================================================
# Save validated data
# ============================================================

df.to_csv(
    OUTPUT_CSV,
    index=False
)

print("\nValidation completed.")
print(f"Saved to: {OUTPUT_CSV}")