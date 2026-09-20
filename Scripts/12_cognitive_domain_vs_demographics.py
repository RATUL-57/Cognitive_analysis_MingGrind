
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

TABLE_DIR = RESULTS_DIR / "tables"
FIGURE_DIR = RESULTS_DIR / "figures"
REPORT_DIR = RESULTS_DIR / "reports"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# INPUT FILES
# ============================================================

GAME_SCORES_FILE = DATA_DIR / "normalized_game_scores.csv"
PLAYERS_FILE = DATA_DIR / "players.csv"


# ============================================================
# OUTPUT FILES
# ============================================================

DOMAIN_DEMOGRAPHIC_FILE = TABLE_DIR / "cognitive_domain_demographic_correlations.csv"
DOMAIN_PLAYER_FILE = TABLE_DIR / "cognitive_domain_player_performance.csv"
REPORT_FILE = REPORT_DIR / "cognitive_domain_vs_demographics.txt"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("COGNITIVE DOMAIN VS DEMOGRAPHIC / LIFESTYLE ANALYSIS")
print("=" * 70)

print("\nLoading data...")

game_scores = pd.read_csv(GAME_SCORES_FILE)
players = pd.read_csv(PLAYERS_FILE)

print(f"Game-score records: {len(game_scores)}")
print(f"Players: {len(players)}")


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_game_columns = [
    "player_id",
    "game_id",
    "game_title",
    "cognitive_skills",
    "normalized_best_score",
    "normalized_average_score"
]

required_player_columns = [
    "player_id",
    "age",
    "weekly_gaming_hours",
    "sleep_hours_last_night"
]

missing_game = [
    col for col in required_game_columns
    if col not in game_scores.columns
]

missing_player = [
    col for col in required_player_columns
    if col not in players.columns
]

if missing_game:
    raise ValueError(
        f"Missing columns in normalized_game_scores.csv: {missing_game}"
    )

if missing_player:
    raise ValueError(
        f"Missing columns in players.csv: {missing_player}"
    )


# ============================================================
# PREPARE NUMERIC VARIABLES
# ============================================================

numeric_columns = [
    "age",
    "weekly_gaming_hours",
    "sleep_hours_last_night"
]

for col in numeric_columns:
    players[col] = pd.to_numeric(players[col], errors="coerce")


# ============================================================
# SPLIT COGNITIVE DOMAINS
# ============================================================

print("\nProcessing cognitive domains...")

# Example:
# "Attention;Reflex"
# becomes:
# Attention
# Reflex

game_scores["cognitive_skills"] = (
    game_scores["cognitive_skills"]
    .fillna("")
    .astype(str)
)

game_scores["domain"] = game_scores["cognitive_skills"].str.split(";")

domain_data = game_scores.explode("domain")

domain_data["domain"] = (
    domain_data["domain"]
    .astype(str)
    .str.strip()
)

# Remove empty domains
domain_data = domain_data[
    domain_data["domain"].notna()
    & (domain_data["domain"] != "")
]


# ============================================================
# CALCULATE GAME-LEVEL DOMAIN PERFORMANCE
# ============================================================

# For each player and domain:
# average the normalized scores of all games
# belonging to that domain.

domain_player = (
    domain_data
    .groupby(["player_id", "domain"], as_index=False)
    .agg(
        domain_best_performance=(
            "normalized_best_score",
            "mean"
        ),
        domain_average_performance=(
            "normalized_average_score",
            "mean"
        ),
        games_in_domain=("game_id", "nunique")
    )
)


# Convert to percentage
domain_player["domain_best_performance"] *= 100
domain_player["domain_average_performance"] *= 100


# ============================================================
# MERGE PLAYER DEMOGRAPHIC / LIFESTYLE DATA
# ============================================================

domain_player = domain_player.merge(
    players[
        [
            "player_id",
            "age",
            "weekly_gaming_hours",
            "sleep_hours_last_night"
        ]
    ],
    on="player_id",
    how="left"
)


# ============================================================
# SAVE PLAYER × DOMAIN DATA
# ============================================================

domain_player.to_csv(
    DOMAIN_PLAYER_FILE,
    index=False
)

print(
    f"\nSaved player-domain dataset:\n"
    f"{DOMAIN_PLAYER_FILE}"
)


# ============================================================
# DOMAINS
# ============================================================

domains = [
    "Attention",
    "Memory",
    "Reasoning",
    "Reflex",
    "Perception",
    "Learning"
]

variables = {
    "Sleep": "sleep_hours_last_night",
    "Age": "age",
    "Gaming Hours": "weekly_gaming_hours"
}


# ============================================================
# SPEARMAN CORRELATION FUNCTION
# ============================================================

def calculate_spearman(data, x_column, y_column):

    subset = data[[x_column, y_column]].dropna()

    n = len(subset)

    # Need at least 3 observations
    if n < 3:
        return np.nan, np.nan, n

    x = subset[x_column]
    y = subset[y_column]

    # Spearman is undefined if either variable is constant
    if x.nunique() <= 1 or y.nunique() <= 1:
        return np.nan, np.nan, n

    result = spearmanr(x, y)

    rho = float(result.statistic)
    p_value = float(result.pvalue)

    return rho, p_value, n


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

print("\nCalculating domain-specific correlations...")

correlation_results = []


for domain in domains:

    domain_subset = domain_player[
        domain_player["domain"] == domain
    ].copy()

    print(f"\n{domain}")
    print("-" * 50)

    for variable_name, variable_column in variables.items():

        rho, p_value, n = calculate_spearman(
            domain_subset,
            variable_column,
            "domain_average_performance"
        )

        correlation_results.append({
            "domain": domain,
            "variable": variable_name,
            "variable_column": variable_column,
            "performance_measure": "domain_average_performance",
            "spearman_rho": rho,
            "p_value": p_value,
            "n": n
        })

        print(
            f"{variable_name:15s} "
            f"rho = {rho if not pd.isna(rho) else 'NA'}   "
            f"p = {p_value if not pd.isna(p_value) else 'NA'}   "
            f"n = {n}"
        )


# ============================================================
# SAVE CORRELATION TABLE
# ============================================================

correlation_df = pd.DataFrame(correlation_results)

correlation_df.to_csv(
    DOMAIN_DEMOGRAPHIC_FILE,
    index=False
)

print(
    f"\nSaved correlation table:\n"
    f"{DOMAIN_DEMOGRAPHIC_FILE}"
)


# ============================================================
# PLOT FUNCTION
# ============================================================

def create_scatter_plot(
    data,
    domain,
    x_column,
    x_label,
    variable_name
):

    plot_data = data[
        [
            x_column,
            "domain_average_performance"
        ]
    ].dropna()

    if len(plot_data) < 2:
        print(
            f"Skipping {domain} vs {variable_name}: "
            f"not enough data."
        )
        return

    x = plot_data[x_column]
    y = plot_data["domain_average_performance"]

    # Calculate Spearman
    rho, p_value, n = calculate_spearman(
        data,
        x_column,
        "domain_average_performance"
    )

    plt.figure(figsize=(7, 5))

    plt.scatter(
        x,
        y,
        alpha=0.75,
        s=45
    )

    plt.xlabel(x_label)
    plt.ylabel("Domain Average Performance (%)")

    plt.title(
        f"{domain} Performance vs {variable_name}"
    )

    # Add correlation information
    if not pd.isna(rho):

        plt.text(
            0.05,
            0.95,
            f"Spearman ρ = {rho:.3f}\n"
            f"p = {p_value:.3f}\n"
            f"n = {n}",
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(
                boxstyle="round",
                facecolor="white",
                alpha=0.8
            )
        )

    plt.grid(
        True,
        alpha=0.25
    )

    plt.tight_layout()

    filename = (
        f"{domain.lower().replace(' ', '_')}"
        f"_vs_{variable_name.lower().replace(' ', '_')}.png"
    )

    output_path = FIGURE_DIR / filename

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Saved: {output_path.name}")


# ============================================================
# GENERATE 18 SCATTER PLOTS
# ============================================================

print("\nGenerating scatter plots...")
print("=" * 70)

for domain in domains:

    domain_subset = domain_player[
        domain_player["domain"] == domain
    ].copy()

    for variable_name, variable_column in variables.items():

        create_scatter_plot(
            data=domain_subset,
            domain=domain,
            x_column=variable_column,
            x_label=variable_name,
            variable_name=variable_name
        )


# ============================================================
# CREATE TEXT REPORT
# ============================================================

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "COGNITIVE DOMAIN VS SLEEP, AGE, AND GAMING HOURS\n"
    )
    f.write("=" * 70 + "\n\n")

    f.write(
        "Purpose\n"
        "-------\n"
    )

    f.write(
        "This analysis examines the relationship between "
        "cognitive-domain performance and three player-level "
        "variables: sleep duration, age, and weekly gaming hours.\n\n"
    )

    f.write(
        "Cognitive-domain performance was calculated by averaging "
        "normalized average scores of games associated with each "
        "domain for each player.\n\n"
    )

    f.write(
        "Spearman rank correlation was used because the sample "
        "size is relatively small and linear-normal assumptions "
        "are not required.\n\n"
    )

    f.write(
        "Correlation Results\n"
        "-------------------\n\n"
    )

    for _, row in correlation_df.iterrows():

        rho = row["spearman_rho"]
        p = row["p_value"]
        n = row["n"]

        rho_text = (
            "NA"
            if pd.isna(rho)
            else f"{rho:.4f}"
        )

        p_text = (
            "NA"
            if pd.isna(p)
            else f"{p:.4f}"
        )

        f.write(
            f"{row['domain']} vs {row['variable']}: "
            f"rho={rho_text}, "
            f"p={p_text}, "
            f"n={n}\n"
        )

    f.write("\n")
    f.write(
        "Interpretation Note\n"
        "-------------------\n\n"
    )

    f.write(
        "The correlations describe associations between "
        "player-level variables and domain-level gameplay "
        "performance. They do not establish causation.\n\n"
    )

    f.write(
        "Because participants did not necessarily play every "
        "game, the number of observations may differ between "
        "cognitive domains. Unplayed games were not treated as "
        "zero-performance observations.\n\n"
    )

    f.write(
        "The cognitive domains represent the intended cognitive "
        "demands of the game activities and should not be "
        "interpreted as clinical measurements of cognitive ability.\n"
    )


# ============================================================
# FINISHED
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print("\nGenerated:")
print("1. Player × cognitive-domain dataset")
print("2. Domain-specific Spearman correlations")
print("3. 18 scatter plots")
print("4. Text report")

print("\nOutput locations:")
print(f"Tables : {TABLE_DIR}")
print(f"Figures: {FIGURE_DIR}")
print(f"Report : {REPORT_FILE}")

