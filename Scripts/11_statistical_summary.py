
from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

TABLES_DIR = RESULTS_DIR / "tables"
REPORTS_DIR = RESULTS_DIR / "reports"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 60)
print("STATISTICAL SUMMARY")
print("=" * 60)


# ============================================================
# HELPER FUNCTION
# ============================================================

def read_csv_if_exists(path):
    """
    Read CSV if it exists.
    Return None if the file is missing.
    """

    if not path.exists():

        print(
            f"[WARNING] File not found: {path}"
        )

        return None

    return pd.read_csv(path)


# ============================================================
# LOAD MAIN DATA
# ============================================================

players = read_csv_if_exists(
    DATA_DIR / "players.csv"
)

scores = read_csv_if_exists(
    DATA_DIR / "normalized_game_scores.csv"
)


if players is None:

    raise FileNotFoundError(
        "players.csv not found. "
        "Run 01_json_to_csv.py first."
    )


if scores is None:

    raise FileNotFoundError(
        "normalized_game_scores.csv not found. "
        "Run 03_clean_and_normalize.py first."
    )


# ============================================================
# LOAD PREVIOUS ANALYSIS RESULTS
# ============================================================

domain_summary = read_csv_if_exists(
    TABLES_DIR /
    "cognitive_domain_performance.csv"
)

game_summary = read_csv_if_exists(
    TABLES_DIR /
    "game_performance.csv"
)

player_summary = read_csv_if_exists(
    TABLES_DIR /
    "player_performance.csv"
)

correlations = read_csv_if_exists(
    TABLES_DIR /
    "spearman_correlations_long.csv"
)


# ============================================================
# DATASET OVERVIEW
# ============================================================

total_players = players[
    "player_id"
].nunique()


total_games = scores[
    "game_id"
].nunique()


games_with_participation = scores[
    scores["play_count"] > 0
]["game_id"].nunique()


player_game_records = len(scores)


total_plays = scores[
    "play_count"
].sum()


games_per_player = (
    scores
    .groupby("player_id")["game_id"]
    .nunique()
)


plays_per_player = (
    scores
    .groupby("player_id")["play_count"]
    .sum()
)


mean_games_per_player = (
    games_per_player.mean()
)


median_games_per_player = (
    games_per_player.median()
)


mean_plays_per_player = (
    plays_per_player.mean()
)


median_plays_per_player = (
    plays_per_player.median()
)


# ============================================================
# OVERALL PERFORMANCE
# ============================================================

average_scores = pd.to_numeric(
    scores["normalized_average_score"],
    errors="coerce"
).dropna()


best_scores = pd.to_numeric(
    scores["normalized_best_score"],
    errors="coerce"
).dropna()


mean_average_performance = (
    average_scores.mean()
)


median_average_performance = (
    average_scores.median()
)


std_average_performance = (
    average_scores.std()
)


mean_best_performance = (
    best_scores.mean()
)


median_best_performance = (
    best_scores.median()
)


std_best_performance = (
    best_scores.std()
)


# ============================================================
# TABLE 1
# OVERALL STATISTICAL SUMMARY
# ============================================================

overall_summary = pd.DataFrame({

    "metric": [

        "Total players",

        "Total games in dataset",

        "Games with participation",

        "Player-game records",

        "Total plays",

        "Mean games per player",

        "Median games per player",

        "Mean plays per player",

        "Median plays per player",

        "Mean normalized average performance",

        "Median normalized average performance",

        "SD normalized average performance",

        "Mean normalized best performance",

        "Median normalized best performance",

        "SD normalized best performance"
    ],

    "value": [

        total_players,

        total_games,

        games_with_participation,

        player_game_records,

        total_plays,

        mean_games_per_player,

        median_games_per_player,

        mean_plays_per_player,

        median_plays_per_player,

        mean_average_performance,

        median_average_performance,

        std_average_performance,

        mean_best_performance,

        median_best_performance,

        std_best_performance
    ]
})


overall_summary.to_csv(
    TABLES_DIR /
    "statistical_overall_summary.csv",
    index=False
)


# ============================================================
# TABLE 2
# COGNITIVE DOMAIN SUMMARY
# ============================================================

if domain_summary is not None:

    domain_output = domain_summary.copy()

    domain_output.to_csv(
        TABLES_DIR /
        "statistical_cognitive_domain_summary.csv",
        index=False
    )

else:

    print(
        "[WARNING] Cognitive domain analysis file missing."
    )


# ============================================================
# TABLE 3
# GAME SUMMARY
# ============================================================

if game_summary is not None:

    game_output = game_summary.copy()

    game_output.to_csv(
        TABLES_DIR /
        "statistical_game_summary.csv",
        index=False
    )

else:

    print(
        "[WARNING] Game performance analysis file missing."
    )


# ============================================================
# TABLE 4
# PLAYER SUMMARY
# ============================================================

if player_summary is not None:

    player_output = player_summary.copy()

    player_output.to_csv(
        TABLES_DIR /
        "statistical_player_summary.csv",
        index=False
    )

else:

    print(
        "[WARNING] Player performance analysis file missing."
    )


# ============================================================
# TABLE 5
# CORRELATION SUMMARY
# ============================================================

if correlations is not None:

    correlation_output = correlations.copy()

    # Make sure numeric columns are numeric
    for column in [
        "rho",
        "p_value",
        "n"
    ]:

        if column in correlation_output.columns:

            correlation_output[column] = pd.to_numeric(
                correlation_output[column],
                errors="coerce"
            )


    # --------------------------------------------------------
    # Remove invalid/undefined correlations
    # only for the ranking table.
    #
    # The original correlation file remains unchanged.
    # --------------------------------------------------------

    valid_correlations = correlation_output[
        correlation_output["rho"].notna()
    ].copy()


    # --------------------------------------------------------
    # Create absolute correlation magnitude
    # --------------------------------------------------------

    if not valid_correlations.empty:

        valid_correlations["absolute_rho"] = (
            valid_correlations["rho"].abs()
        )


        # Sort strongest correlations first
        valid_correlations = (
            valid_correlations
            .sort_values(
                by="absolute_rho",
                ascending=False
            )
        )


        # Remove helper column
        valid_correlations = (
            valid_correlations
            .drop(columns=["absolute_rho"])
        )


    # --------------------------------------------------------
    # Save correlation summary
    # --------------------------------------------------------

    valid_correlations.to_csv(
        TABLES_DIR /
        "statistical_correlation_summary.csv",
        index=False
    )


    print(
        f"Valid correlations summarized: "
        f"{len(valid_correlations)}"
    )

    print(
        f"Undefined correlations ignored: "
        f"{len(correlation_output) - len(valid_correlations)}"
    )


else:

    print(
        "[WARNING] spearman_correlations_long.csv "
        "was not found."
    )

    print(
        "[INFO] Run 10_correlation_analysis.py first."
    )


# ============================================================
# TABLE 6
# DESCRIPTIVE STATISTICS
# ============================================================

descriptive_rows = []


# ------------------------------------------------------------
# Player demographic variables
# ------------------------------------------------------------

demographic_variables = [

    "age",

    "weekly_gaming_hours",

    "sleep_hours_last_night"
]


for variable in demographic_variables:

    if variable not in players.columns:
        continue


    values = pd.to_numeric(
        players[variable],
        errors="coerce"
    ).dropna()


    if len(values) == 0:
        continue


    descriptive_rows.append({

        "variable": variable,

        "n": len(values),

        "mean": values.mean(),

        "median": values.median(),

        "std": values.std(),

        "min": values.min(),

        "max": values.max()
    })


# ------------------------------------------------------------
# Overall game performance
# ------------------------------------------------------------

if len(average_scores) > 0:

    descriptive_rows.append({

        "variable":
            "normalized_average_score",

        "n":
            len(average_scores),

        "mean":
            average_scores.mean(),

        "median":
            average_scores.median(),

        "std":
            average_scores.std(),

        "min":
            average_scores.min(),

        "max":
            average_scores.max()
    })


if len(best_scores) > 0:

    descriptive_rows.append({

        "variable":
            "normalized_best_score",

        "n":
            len(best_scores),

        "mean":
            best_scores.mean(),

        "median":
            best_scores.median(),

        "std":
            best_scores.std(),

        "min":
            best_scores.min(),

        "max":
            best_scores.max()
    })


descriptive_summary = pd.DataFrame(
    descriptive_rows
)


descriptive_summary.to_csv(
    TABLES_DIR /
    "statistical_descriptive_summary.csv",
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

report_path = (
    REPORTS_DIR /
    "statistical_summary.txt"
)


with open(
    report_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "STATISTICAL SUMMARY\n"
    )

    f.write(
        "=" * 70 + "\n\n"
    )


    # --------------------------------------------------------
    # Dataset overview
    # --------------------------------------------------------

    f.write(
        "DATASET OVERVIEW\n"
    )

    f.write(
        "-" * 70 + "\n"
    )

    f.write(
        f"Total players: "
        f"{total_players}\n"
    )

    f.write(
        f"Total games in dataset: "
        f"{total_games}\n"
    )

    f.write(
        f"Games with participation: "
        f"{games_with_participation}\n"
    )

    f.write(
        f"Player-game records: "
        f"{player_game_records}\n"
    )

    f.write(
        f"Total plays: "
        f"{total_plays}\n"
    )

    f.write(
        f"Mean games per player: "
        f"{mean_games_per_player:.2f}\n"
    )

    f.write(
        f"Median games per player: "
        f"{median_games_per_player:.2f}\n"
    )

    f.write(
        f"Mean plays per player: "
        f"{mean_plays_per_player:.2f}\n"
    )

    f.write(
        f"Median plays per player: "
        f"{median_plays_per_player:.2f}\n"
    )


    # --------------------------------------------------------
    # Overall performance
    # --------------------------------------------------------

    f.write(
        "\nOVERALL PERFORMANCE\n"
    )

    f.write(
        "-" * 70 + "\n"
    )

    f.write(
        f"Mean normalized average performance: "
        f"{mean_average_performance:.4f}\n"
    )

    f.write(
        f"Median normalized average performance: "
        f"{median_average_performance:.4f}\n"
    )

    f.write(
        f"SD normalized average performance: "
        f"{std_average_performance:.4f}\n"
    )

    f.write(
        f"Mean normalized best performance: "
        f"{mean_best_performance:.4f}\n"
    )

    f.write(
        f"Median normalized best performance: "
        f"{median_best_performance:.4f}\n"
    )

    f.write(
        f"SD normalized best performance: "
        f"{std_best_performance:.4f}\n"
    )


    # --------------------------------------------------------
    # Analysis availability
    # --------------------------------------------------------

    f.write(
        "\nANALYSIS AVAILABILITY\n"
    )

    f.write(
        "-" * 70 + "\n"
    )

    f.write(
        "Cognitive domain analysis: "
        + (
            "Available\n"
            if domain_summary is not None
            else "Missing\n"
        )
    )

    f.write(
        "Game performance analysis: "
        + (
            "Available\n"
            if game_summary is not None
            else "Missing\n"
        )
    )

    f.write(
        "Player performance analysis: "
        + (
            "Available\n"
            if player_summary is not None
            else "Missing\n"
        )
    )

    f.write(
        "Correlation analysis: "
        + (
            "Available\n"
            if correlations is not None
            else "Missing\n"
        )
    )


    # --------------------------------------------------------
    # Methodological notes
    # --------------------------------------------------------

    f.write(
        "\nMETHODOLOGICAL NOTES\n"
    )

    f.write(
        "-" * 70 + "\n"
    )

    f.write(
        "1. Scores are normalized relative to each game's "
        "maximum score.\n"
    )

    f.write(
        "2. Unplayed games are not treated as zero performance.\n"
    )

    f.write(
        "3. Cognitive-domain assignments are based on the "
        "game design.\n"
    )

    f.write(
        "4. Cognitive-domain labels should not be interpreted "
        "as clinically validated cognitive measurements.\n"
    )

    f.write(
        "5. Spearman correlations are exploratory and do not "
        "establish causal relationships.\n"
    )

    f.write(
        "6. Undefined correlations occur when a variable has "
        "no variation among the available observations.\n"
    )

    f.write(
        "7. The current aggregate logs do not provide "
        "attempt-level learning curves.\n"
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("STATISTICAL SUMMARY COMPLETED")
print("=" * 60)

print("\nGenerated files:")

print(
    "1.",
    TABLES_DIR /
    "statistical_overall_summary.csv"
)

if domain_summary is not None:

    print(
        "2.",
        TABLES_DIR /
        "statistical_cognitive_domain_summary.csv"
    )

if game_summary is not None:

    print(
        "3.",
        TABLES_DIR /
        "statistical_game_summary.csv"
    )

if player_summary is not None:

    print(
        "4.",
        TABLES_DIR /
        "statistical_player_summary.csv"
    )

if correlations is not None:

    print(
        "5.",
        TABLES_DIR /
        "statistical_correlation_summary.csv"
    )

print(
    "6.",
    TABLES_DIR /
    "statistical_descriptive_summary.csv"
)

print(
    "\nReport:",
    report_path
)

print("\nDone.")

