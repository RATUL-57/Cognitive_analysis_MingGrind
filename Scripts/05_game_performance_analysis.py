from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


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

INPUT_CSV = DATA_DIR / "normalized_game_scores.csv"


# ============================================================
# Load data
# ============================================================

df = pd.read_csv(INPUT_CSV)

print("=" * 60)
print("GAME PERFORMANCE ANALYSIS")
print("=" * 60)

print(f"Records: {len(df)}")


# ============================================================
# Game-level performance
# ============================================================

game_performance = (
    df.groupby(
        [
            "game_id",
            "game_title",
            "game_type",
            "cognitive_skills",
            "max_score"
        ],
        as_index=False
    )
    .agg(
        participants=("player_id", "nunique"),

        mean_best_score=(
            "normalized_best_score",
            "mean"
        ),

        median_best_score=(
            "normalized_best_score",
            "median"
        ),

        std_best_score=(
            "normalized_best_score",
            "std"
        ),

        mean_average_score=(
            "normalized_average_score",
            "mean"
        ),

        median_average_score=(
            "normalized_average_score",
            "median"
        ),

        std_average_score=(
            "normalized_average_score",
            "std"
        ),

        total_plays=("play_count", "sum"),

        mean_play_count=("play_count", "mean")
    )
)


# ============================================================
# Convert performance to percentage
# ============================================================

game_performance["mean_best_percent"] = (
    game_performance["mean_best_score"] * 100
)

game_performance["mean_average_percent"] = (
    game_performance["mean_average_score"] * 100
)

game_performance["median_average_percent"] = (
    game_performance["median_average_score"] * 100
)


# ============================================================
# Round values
# ============================================================

numeric_columns = [
    "mean_best_score",
    "median_best_score",
    "std_best_score",
    "mean_average_score",
    "median_average_score",
    "std_average_score",
    "mean_play_count",
    "mean_best_percent",
    "mean_average_percent",
    "median_average_percent"
]

for column in numeric_columns:
    game_performance[column] = (
        game_performance[column].round(4)
    )


game_performance = game_performance.sort_values(
    "game_id"
)


# ============================================================
# Save complete game performance table
# ============================================================

game_performance.to_csv(
    TABLES_DIR / "game_performance.csv",
    index=False
)


# ============================================================
# Figure 1: Mean normalized average performance
# ============================================================

plot_data = game_performance.sort_values(
    "mean_average_percent",
    ascending=True
)

plt.figure(figsize=(11, 8))

plt.barh(
    plot_data["game_title"],
    plot_data["mean_average_percent"]
)

plt.xlabel("Mean Average Score (%)")
plt.ylabel("Game")
plt.title("Mean Normalized Performance by Game")
plt.xlim(0, 100)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "mean_performance_by_game.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 2: Best vs average performance
# ============================================================

plot_data = game_performance.sort_values(
    "game_id"
)

x = range(len(plot_data))

plt.figure(figsize=(13, 7))

plt.plot(
    x,
    plot_data["mean_best_percent"],
    marker="o",
    label="Mean Best Score"
)

plt.plot(
    x,
    plot_data["mean_average_percent"],
    marker="o",
    label="Mean Average Score"
)

plt.xticks(
    list(x),
    plot_data["game_title"],
    rotation=75,
    ha="right"
)

plt.ylabel("Score (%)")
plt.xlabel("Game")
plt.title("Mean Best Score vs Mean Average Score")
plt.ylim(0, 100)
plt.legend()

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "best_vs_average_game_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Report
# ============================================================

report_path = REPORTS_DIR / "game_performance_analysis.txt"

with open(report_path, "w", encoding="utf-8") as f:

    f.write("GAME PERFORMANCE ANALYSIS REPORT\n")
    f.write("=" * 60 + "\n\n")

    f.write(
        "Scores are normalized according to each game's maximum "
        "possible score.\n\n"
    )

    f.write("Game-level results:\n")
    f.write("-" * 60 + "\n")

    for _, row in game_performance.iterrows():

        f.write(
            f"{row['game_id']:>2} | "
            f"{row['game_title']:<25} | "
            f"Participants: {row['participants']:>3} | "
            f"Mean Average: "
            f"{row['mean_average_percent']:.2f}% | "
            f"Mean Best: "
            f"{row['mean_best_percent']:.2f}%\n"
        )


print("\nGame performance analysis completed.")
print(f"Table:   {TABLES_DIR / 'game_performance.csv'}")
print(f"Figures: {FIGURES_DIR}")
print(f"Report:  {report_path}")