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
# Input files
# ============================================================

SCORES_CSV = DATA_DIR / "normalized_game_scores.csv"
PLAYERS_CSV = DATA_DIR / "players.csv"


# ============================================================
# Load data
# ============================================================

scores = pd.read_csv(SCORES_CSV)
players = pd.read_csv(PLAYERS_CSV)

print("=" * 60)
print("PLAYER PERFORMANCE ANALYSIS")
print("=" * 60)


# ============================================================
# Calculate best-average gap
# ============================================================

scores["best_average_gap"] = (
    scores["normalized_best_score"]
    - scores["normalized_average_score"]
)


# ============================================================
# Player-level performance
# ============================================================

player_performance = (
    scores.groupby("player_id", as_index=False)
    .agg(
        games_played=("game_id", "nunique"),

        total_plays=("play_count", "sum"),

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

        mean_best_score=(
            "normalized_best_score",
            "mean"
        ),

        median_best_score=(
            "normalized_best_score",
            "median"
        ),

        mean_best_average_gap=(
            "best_average_gap",
            "mean"
        )
    )
)


# ============================================================
# Convert performance to percentage
# ============================================================

player_performance["mean_average_percent"] = (
    player_performance["mean_average_score"] * 100
)

player_performance["median_average_percent"] = (
    player_performance["median_average_score"] * 100
)

player_performance["mean_best_percent"] = (
    player_performance["mean_best_score"] * 100
)

player_performance["mean_best_average_gap_percent"] = (
    player_performance["mean_best_average_gap"] * 100
)


# ============================================================
# Round values
# ============================================================

numeric_columns = [
    "mean_average_score",
    "median_average_score",
    "std_average_score",
    "mean_best_score",
    "median_best_score",
    "mean_best_average_gap",
    "mean_average_percent",
    "median_average_percent",
    "mean_best_percent",
    "mean_best_average_gap_percent"
]

for column in numeric_columns:
    player_performance[column] = (
        player_performance[column].round(4)
    )


# ============================================================
# Add player demographic information
# ============================================================

player_info_columns = [
    "player_id",
    "age",
    "gender",
    "country",
    "favorite_genre",
    "weekly_gaming_hours",
    "sleep_hours_last_night"
]

player_info = players[player_info_columns].copy()

player_performance = player_info.merge(
    player_performance,
    on="player_id",
    how="right"
)


# ============================================================
# Save player performance table
# ============================================================

player_performance.to_csv(
    TABLES_DIR / "player_performance.csv",
    index=False
)


# ============================================================
# Overall player statistics
# ============================================================

overall_summary = pd.DataFrame({
    "metric": [
        "Number of players",
        "Mean games played",
        "Median games played",
        "Mean total plays",
        "Mean normalized average performance",
        "Median normalized average performance",
        "Mean normalized best performance"
    ],

    "value": [
        len(player_performance),

        player_performance["games_played"].mean(),

        player_performance["games_played"].median(),

        player_performance["total_plays"].mean(),

        player_performance["mean_average_score"].mean(),

        player_performance["mean_average_score"].median(),

        player_performance["mean_best_score"].mean()
    ]
})

overall_summary["value"] = (
    overall_summary["value"].round(4)
)

overall_summary.to_csv(
    TABLES_DIR / "overall_player_performance.csv",
    index=False
)


# ============================================================
# Figure 1: Distribution of player performance
# ============================================================

plt.figure(figsize=(9, 6))

plt.hist(
    player_performance["mean_average_percent"],
    bins=10
)

plt.xlabel("Mean Average Performance (%)")
plt.ylabel("Number of Players")
plt.title("Distribution of Overall Player Performance")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "player_performance_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 2: Games played vs performance
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    player_performance["games_played"],
    player_performance["mean_average_percent"]
)

plt.xlabel("Number of Games Played")
plt.ylabel("Mean Average Performance (%)")
plt.title("Game Participation vs Overall Performance")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "games_played_vs_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 3: Total plays vs performance
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    player_performance["total_plays"],
    player_performance["mean_average_percent"]
)

plt.xlabel("Total Plays")
plt.ylabel("Mean Average Performance (%)")
plt.title("Total Play Count vs Overall Performance")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "play_count_vs_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Report
# ============================================================

report_path = REPORTS_DIR / "player_performance_analysis.txt"

with open(report_path, "w", encoding="utf-8") as f:

    f.write("PLAYER PERFORMANCE ANALYSIS REPORT\n")
    f.write("=" * 60 + "\n\n")

    f.write(
        "Player performance is calculated using the normalized "
        "average score across games actually played by each player.\n"
    )

    f.write(
        "Unplayed games are not treated as zero.\n\n"
    )

    f.write("Overall statistics:\n")
    f.write("-" * 60 + "\n")

    for _, row in overall_summary.iterrows():
        f.write(
            f"{row['metric']}: {row['value']}\n"
        )

    f.write("\nPlayer-level results:\n")
    f.write("-" * 60 + "\n")

    for _, row in player_performance.iterrows():

        f.write(
            f"{row['player_id']} | "
            f"Games: {row['games_played']} | "
            f"Plays: {row['total_plays']} | "
            f"Mean Performance: "
            f"{row['mean_average_percent']:.2f}%\n"
        )


print("\nPlayer performance analysis completed.")
print(f"Table:   {TABLES_DIR / 'player_performance.csv'}")
print(f"Figures: {FIGURES_DIR}")
print(f"Report:  {report_path}")