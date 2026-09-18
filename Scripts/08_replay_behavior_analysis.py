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
print("REPLAY BEHAVIOR ANALYSIS")
print("=" * 60)


# ============================================================
# Calculate performance gap
# ============================================================

df["best_average_gap"] = (
    df["normalized_best_score"]
    - df["normalized_average_score"]
)

df["best_average_gap_percent"] = (
    df["best_average_gap"] * 100
)


# ============================================================
# Replay category
# ============================================================

def classify_replay(play_count):

    if play_count == 1:
        return "Single play"

    elif play_count == 2:
        return "2 plays"

    elif play_count == 3:
        return "3 plays"

    else:
        return "4+ plays"


df["replay_category"] = (
    df["play_count"]
    .apply(classify_replay)
)


# ============================================================
# Replay category analysis
# ============================================================

replay_analysis = (
    df.groupby(
        "replay_category",
        as_index=False
    )
    .agg(
        player_game_records=("player_id", "size"),

        unique_players=("player_id", "nunique"),

        mean_play_count=("play_count", "mean"),

        mean_average_score=(
            "normalized_average_score",
            "mean"
        ),

        median_average_score=(
            "normalized_average_score",
            "median"
        ),

        mean_best_score=(
            "normalized_best_score",
            "mean"
        ),

        mean_best_average_gap=(
            "best_average_gap",
            "mean"
        )
    )
)


# ============================================================
# Convert to percentages
# ============================================================

replay_analysis["mean_average_percent"] = (
    replay_analysis["mean_average_score"] * 100
)

replay_analysis["median_average_percent"] = (
    replay_analysis["median_average_score"] * 100
)

replay_analysis["mean_best_percent"] = (
    replay_analysis["mean_best_score"] * 100
)

replay_analysis["mean_best_average_gap_percent"] = (
    replay_analysis["mean_best_average_gap"] * 100
)


# ============================================================
# Save replay summary
# ============================================================

replay_analysis.to_csv(
    TABLES_DIR / "replay_category_analysis.csv",
    index=False
)


# ============================================================
# Game-specific replay analysis
# ============================================================

game_replay = (
    df.groupby(
        [
            "game_id",
            "game_title"
        ],
        as_index=False
    )
    .agg(
        participants=("player_id", "nunique"),

        mean_play_count=("play_count", "mean"),

        median_play_count=("play_count", "median"),

        max_play_count=("play_count", "max"),

        mean_average_score=(
            "normalized_average_score",
            "mean"
        ),

        mean_best_score=(
            "normalized_best_score",
            "mean"
        ),

        mean_best_average_gap=(
            "best_average_gap",
            "mean"
        )
    )
)


game_replay["mean_average_percent"] = (
    game_replay["mean_average_score"] * 100
)

game_replay["mean_best_percent"] = (
    game_replay["mean_best_score"] * 100
)

game_replay["mean_best_average_gap_percent"] = (
    game_replay["mean_best_average_gap"] * 100
)


game_replay.to_csv(
    TABLES_DIR / "game_replay_behavior.csv",
    index=False
)


# ============================================================
# Figure 1: Play count vs performance
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    df["play_count"],
    df["normalized_average_score"] * 100
)

plt.xlabel("Play Count")
plt.ylabel("Normalized Average Performance (%)")
plt.title("Replay Count vs Performance")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "replay_count_vs_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 2: Replay category performance
# ============================================================

category_order = [
    "Single play",
    "2 plays",
    "3 plays",
    "4+ plays"
]

plot_data = replay_analysis.copy()

plot_data["order"] = plot_data[
    "replay_category"
].map(
    {
        category: index
        for index, category in enumerate(category_order)
    }
)

plot_data = plot_data.sort_values("order")


plt.figure(figsize=(9, 6))

plt.bar(
    plot_data["replay_category"],
    plot_data["mean_average_percent"]
)

plt.xlabel("Replay Category")
plt.ylabel("Mean Average Performance (%)")
plt.title("Performance by Replay Category")
plt.ylim(0, 100)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "performance_by_replay_category.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 3: Best-average gap vs play count
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    df["play_count"],
    df["best_average_gap_percent"]
)

plt.xlabel("Play Count")
plt.ylabel("Best - Average Score Gap (%)")
plt.title("Replay Count vs Best-Average Performance Gap")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "replay_count_vs_best_average_gap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Report
# ============================================================

report_path = REPORTS_DIR / "replay_behavior_analysis.txt"

with open(report_path, "w", encoding="utf-8") as f:

    f.write("REPLAY BEHAVIOR ANALYSIS REPORT\n")
    f.write("=" * 60 + "\n\n")

    f.write(
        "This analysis examines associations between play count "
        "and normalized performance.\n\n"
    )

    f.write(
        "Important limitation: the current dataset contains "
        "aggregate bestScore, averageScore and playCount only. "
        "Therefore, this analysis cannot establish whether "
        "performance improved from one attempt to the next.\n\n"
    )

    f.write("Replay category results:\n")
    f.write("-" * 60 + "\n")

    for _, row in replay_analysis.iterrows():

        f.write(
            f"{row['replay_category']:<15} | "
            f"Records: {row['player_game_records']:>3} | "
            f"Mean plays: {row['mean_play_count']:.2f} | "
            f"Mean performance: "
            f"{row['mean_average_percent']:.2f}%\n"
        )


print("\nReplay behavior analysis completed.")
print(
    f"Tables: {TABLES_DIR}"
)
print(
    f"Figures: {FIGURES_DIR}"
)
print(
    f"Report: {report_path}"
)