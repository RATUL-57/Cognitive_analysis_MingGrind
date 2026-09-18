from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RESULTS_DIR = PROJECT_ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"

for directory in [TABLES_DIR, FIGURES_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# Input
# ============================================================

PERFORMANCE_CSV = (
    DATA_DIR / "normalized_game_scores.csv"
)

PLAYERS_CSV = (
    DATA_DIR / "players.csv"
)


# ============================================================
# Load data
# ============================================================

scores = pd.read_csv(PERFORMANCE_CSV)
players = pd.read_csv(PLAYERS_CSV)


# ============================================================
# Calculate player-level performance
# ============================================================

player_performance = (
    scores.groupby(
        "player_id",
        as_index=False
    )
    .agg(
        mean_performance=(
            "normalized_average_score",
            "mean"
        ),
        mean_best_performance=(
            "normalized_best_score",
            "mean"
        ),
        games_played=(
            "game_id",
            "nunique"
        ),
        total_plays=(
            "play_count",
            "sum"
        )
    )
)


# ============================================================
# Merge demographics
# ============================================================

df = players.merge(
    player_performance,
    on="player_id",
    how="inner"
)

df["performance_percent"] = (
    df["mean_performance"] * 100
)

df["best_performance_percent"] = (
    df["mean_best_performance"] * 100
)


print("=" * 60)
print("DEMOGRAPHIC ANALYSIS")
print("=" * 60)

print(f"Players included: {len(df)}")


# ============================================================
# Spearman correlations
# ============================================================

numeric_variables = [
    "age",
    "weekly_gaming_hours",
    "sleep_hours_last_night",
    "games_played",
    "total_plays"
]

correlation_results = []


for variable in numeric_variables:

    temp = df[
        [
            variable,
            "mean_performance"
        ]
    ].dropna()

    if len(temp) < 3:
        continue

    rho, p_value = spearmanr(
        temp[variable],
        temp["mean_performance"]
    )

    correlation_results.append({
        "variable": variable,
        "n": len(temp),
        "spearman_rho": rho,
        "p_value": p_value
    })


correlation_df = pd.DataFrame(
    correlation_results
)

if not correlation_df.empty:

    correlation_df[
        [
            "spearman_rho",
            "p_value"
        ]
    ] = correlation_df[
        [
            "spearman_rho",
            "p_value"
        ]
    ].round(4)


correlation_df.to_csv(
    TABLES_DIR / "demographic_spearman_correlations.csv",
    index=False
)


# ============================================================
# Categorical group analysis function
# ============================================================

def categorical_performance_analysis(
    data,
    column
):

    result = (
        data.groupby(
            column,
            dropna=False
        )
        .agg(
            participants=(
                "player_id",
                "nunique"
            ),

            mean_performance=(
                "mean_performance",
                "mean"
            ),

            median_performance=(
                "mean_performance",
                "median"
            ),

            mean_games_played=(
                "games_played",
                "mean"
            ),

            mean_total_plays=(
                "total_plays",
                "mean"
            )
        )
        .reset_index()
    )

    result["mean_performance_percent"] = (
        result["mean_performance"] * 100
    )

    result["median_performance_percent"] = (
        result["median_performance"] * 100
    )

    return result


# ============================================================
# Gender analysis
# ============================================================

gender_analysis = categorical_performance_analysis(
    df,
    "gender"
)

gender_analysis.to_csv(
    TABLES_DIR / "performance_by_gender.csv",
    index=False
)


# ============================================================
# Country analysis
# ============================================================

country_analysis = categorical_performance_analysis(
    df,
    "country"
)

country_analysis.to_csv(
    TABLES_DIR / "performance_by_country.csv",
    index=False
)


# ============================================================
# Favorite genre analysis
# ============================================================

genre_analysis = categorical_performance_analysis(
    df,
    "favorite_genre"
)

genre_analysis.to_csv(
    TABLES_DIR / "performance_by_favorite_genre.csv",
    index=False
)


# ============================================================
# Figure 1: Age vs performance
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    df["age"],
    df["performance_percent"]
)

plt.xlabel("Age")
plt.ylabel("Mean Performance (%)")
plt.title("Age vs Overall Performance")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "age_vs_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 2: Gaming hours vs performance
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    df["weekly_gaming_hours"],
    df["performance_percent"]
)

plt.xlabel("Weekly Gaming Hours")
plt.ylabel("Mean Performance (%)")
plt.title("Weekly Gaming Hours vs Overall Performance")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "gaming_hours_vs_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 3: Sleep vs performance
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    df["sleep_hours_last_night"],
    df["performance_percent"]
)

plt.xlabel("Sleep Hours Last Night")
plt.ylabel("Mean Performance (%)")
plt.title("Sleep Duration vs Overall Performance")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "sleep_vs_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 4: Performance by gender
# ============================================================

gender_plot = gender_analysis.dropna(
    subset=["gender"]
)

plt.figure(figsize=(8, 6))

plt.bar(
    gender_plot["gender"].astype(str),
    gender_plot["mean_performance_percent"]
)

plt.xlabel("Gender")
plt.ylabel("Mean Performance (%)")
plt.title("Performance by Gender")
plt.ylim(0, 100)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "performance_by_gender.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 5: Performance by favorite genre
# ============================================================

genre_plot = genre_analysis.dropna(
    subset=["favorite_genre"]
)

plt.figure(figsize=(10, 6))

plt.bar(
    genre_plot["favorite_genre"].astype(str),
    genre_plot["mean_performance_percent"]
)

plt.xlabel("Favorite Genre")
plt.ylabel("Mean Performance (%)")
plt.title("Performance by Favorite Game Genre")
plt.xticks(rotation=30)
plt.ylim(0, 100)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "performance_by_favorite_genre.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Report
# ============================================================

report_path = REPORTS_DIR / "demographic_analysis.txt"

with open(
    report_path,
    "w",
    encoding="utf-8"
) as f:

    f.write("DEMOGRAPHIC AND BEHAVIORAL ANALYSIS REPORT\n")
    f.write("=" * 60 + "\n\n")

    f.write(
        "Performance is calculated as the mean normalized "
        "average score across games played by each participant.\n\n"
    )

    f.write(
        "Numerical associations use Spearman correlation. "
        "Categorical variables are summarized descriptively.\n\n"
    )

    f.write("Spearman correlations:\n")
    f.write("-" * 60 + "\n")

    for _, row in correlation_df.iterrows():

        f.write(
            f"{row['variable']:<25} | "
            f"n={int(row['n']):>3} | "
            f"rho={row['spearman_rho']:.4f} | "
            f"p={row['p_value']:.4f}\n"
        )

    f.write("\nPerformance by gender:\n")
    f.write("-" * 60 + "\n")

    for _, row in gender_analysis.iterrows():

        f.write(
            f"{row['gender']} | "
            f"n={row['participants']} | "
            f"Mean={row['mean_performance_percent']:.2f}%\n"
        )

    f.write("\nPerformance by country:\n")
    f.write("-" * 60 + "\n")

    for _, row in country_analysis.iterrows():

        f.write(
            f"{row['country']} | "
            f"n={row['participants']} | "
            f"Mean={row['mean_performance_percent']:.2f}%\n"
        )

    f.write("\nPerformance by favorite genre:\n")
    f.write("-" * 60 + "\n")

    for _, row in genre_analysis.iterrows():

        f.write(
            f"{row['favorite_genre']} | "
            f"n={row['participants']} | "
            f"Mean={row['mean_performance_percent']:.2f}%\n"
        )


print("\nDemographic analysis completed.")
print(
    f"Tables: {TABLES_DIR}"
)
print(
    f"Figures: {FIGURES_DIR}"
)
print(
    f"Report: {report_path}"
)