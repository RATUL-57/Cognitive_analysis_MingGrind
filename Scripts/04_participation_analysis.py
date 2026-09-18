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

PLAYERS_CSV = DATA_DIR / "players.csv"
GAME_SCORES_CSV = DATA_DIR / "game_scores.csv"


# ============================================================
# Load data
# ============================================================

players = pd.read_csv(PLAYERS_CSV)
scores = pd.read_csv(GAME_SCORES_CSV)

total_players = players["player_id"].nunique()

print("=" * 60)
print("PARTICIPATION ANALYSIS")
print("=" * 60)

print(f"Total players: {total_players}")


# ============================================================
# Game participation
# ============================================================

participation = (
    scores.groupby(
        [
            "game_id",
            "game_title",
            "game_type",
            "cognitive_skills"
        ],
        as_index=False
    )
    .agg(
        participants=("player_id", "nunique"),
        total_plays=("play_count", "sum"),
        average_plays_per_player=("play_count", "mean")
    )
)

participation["participation_percent"] = (
    participation["participants"] / total_players * 100
)

participation["average_plays_per_player"] = (
    participation["average_plays_per_player"].round(2)
)

participation["participation_percent"] = (
    participation["participation_percent"].round(2)
)

participation = participation.sort_values(
    "game_id"
)


# ============================================================
# Save participation table
# ============================================================

participation.to_csv(
    TABLES_DIR / "game_participation.csv",
    index=False
)


# ============================================================
# Player participation summary
# ============================================================

player_participation = (
    scores.groupby("player_id")
    .agg(
        games_played=("game_id", "nunique"),
        total_plays=("play_count", "sum")
    )
    .reset_index()
)

player_participation["games_played_percent"] = (
    player_participation["games_played"] / 25 * 100
)

player_participation["games_played_percent"] = (
    player_participation["games_played_percent"].round(2)
)

player_participation.to_csv(
    TABLES_DIR / "player_participation.csv",
    index=False
)


# ============================================================
# Overall participation statistics
# ============================================================

overall = pd.DataFrame({
    "metric": [
        "Total players",
        "Total games",
        "Games with participation",
        "Total recorded plays",
        "Average games played per player",
        "Average plays per player"
    ],
    "value": [
        total_players,
        25,
        participation["game_id"].nunique(),
        scores["play_count"].sum(),
        player_participation["games_played"].mean(),
        player_participation["total_plays"].mean()
    ]
})

overall["value"] = overall["value"].round(2)

overall.to_csv(
    TABLES_DIR / "overall_participation_summary.csv",
    index=False
)


# ============================================================
# Figure 1: Participation percentage by game
# ============================================================

plot_data = participation.sort_values(
    "participation_percent",
    ascending=True
)

plt.figure(figsize=(11, 8))

plt.barh(
    plot_data["game_title"],
    plot_data["participation_percent"]
)

plt.xlabel("Participation (%)")
plt.ylabel("Game")
plt.title("Player Participation by Game")
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "game_participation_percentage.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 2: Total plays by game
# ============================================================

plot_data = participation.sort_values(
    "total_plays",
    ascending=True
)

plt.figure(figsize=(11, 8))

plt.barh(
    plot_data["game_title"],
    plot_data["total_plays"]
)

plt.xlabel("Total Plays")
plt.ylabel("Game")
plt.title("Total Plays by Game")
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "total_plays_by_game.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Report
# ============================================================

report_path = REPORTS_DIR / "participation_analysis.txt"

with open(report_path, "w", encoding="utf-8") as f:

    f.write("PARTICIPATION ANALYSIS REPORT\n")
    f.write("=" * 60 + "\n\n")

    f.write(f"Total players: {total_players}\n")
    f.write(f"Total games: 25\n")
    f.write(
        f"Games with participation: "
        f"{participation['game_id'].nunique()}\n"
    )
    f.write(
        f"Total recorded plays: "
        f"{scores['play_count'].sum()}\n"
    )

    f.write("\nAverage games played per player: ")
    f.write(
        f"{player_participation['games_played'].mean():.2f}\n"
    )

    f.write("\nGame participation:\n")
    f.write("-" * 60 + "\n")

    for _, row in participation.iterrows():
        f.write(
            f"{row['game_id']:>2} | "
            f"{row['game_title']:<25} | "
            f"{row['participants']} players | "
            f"{row['participation_percent']:.2f}% | "
            f"{row['total_plays']} plays\n"
        )


print("\nParticipation analysis completed.")
print(f"Tables:  {TABLES_DIR}")
print(f"Figures: {FIGURES_DIR}")
print(f"Report:  {report_path}")