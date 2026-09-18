from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 60)
print("CORRELATION ANALYSIS")
print("=" * 60)


# ============================================================
# LOAD DATA
# ============================================================

players = pd.read_csv(
    DATA_DIR / "players.csv"
)

scores = pd.read_csv(
    DATA_DIR / "normalized_game_scores.csv"
)


# ============================================================
# BASIC VALIDATION
# ============================================================

required_player_columns = [
    "player_id",
    "age",
    "weekly_gaming_hours",
    "sleep_hours_last_night"
]

required_score_columns = [
    "player_id",
    "game_id",
    "normalized_average_score",
    "normalized_best_score",
    "cognitive_skills"
]

for column in required_player_columns:

    if column not in players.columns:
        raise ValueError(
            f"Missing column in players.csv: {column}"
        )


for column in required_score_columns:

    if column not in scores.columns:
        raise ValueError(
            f"Missing column in normalized_game_scores.csv: {column}"
        )


# ============================================================
# PLAYER-LEVEL OVERALL PERFORMANCE
# ============================================================

player_performance = (
    scores
    .groupby("player_id")
    .agg(
        overall_performance=(
            "normalized_average_score",
            "mean"
        ),
        overall_best_performance=(
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
    .reset_index()
)


# ============================================================
# PLAYER × COGNITIVE DOMAIN PERFORMANCE
# ============================================================

domain_rows = []

for _, row in scores.iterrows():

    player_id = row["player_id"]

    skills = str(row["cognitive_skills"])

    # Handle missing/empty skill field
    if (
        skills.lower() == "nan"
        or skills.strip() == ""
    ):
        continue

    skill_list = [
        skill.strip()
        for skill in skills.split(";")
        if skill.strip()
    ]

    for skill in skill_list:

        domain_rows.append({
            "player_id": player_id,
            "cognitive_domain": skill,
            "normalized_average_score":
                row["normalized_average_score"]
        })


domain_long = pd.DataFrame(domain_rows)


# ============================================================
# CREATE PLAYER × DOMAIN TABLE
# ============================================================

if not domain_long.empty:

    domain_player = (
        domain_long
        .groupby(
            ["player_id", "cognitive_domain"]
        )["normalized_average_score"]
        .mean()
        .reset_index()
    )

    domain_wide = (
        domain_player
        .pivot(
            index="player_id",
            columns="cognitive_domain",
            values="normalized_average_score"
        )
        .reset_index()
    )

else:

    domain_wide = pd.DataFrame(
        columns=["player_id"]
    )


# ============================================================
# MERGE ALL PLAYER-LEVEL VARIABLES
# ============================================================

analysis_df = players.merge(
    player_performance,
    on="player_id",
    how="left"
)

analysis_df = analysis_df.merge(
    domain_wide,
    on="player_id",
    how="left"
)


# ============================================================
# VARIABLES FOR CORRELATION
# ============================================================

candidate_variables = [
    "age",
    "weekly_gaming_hours",
    "sleep_hours_last_night",
    "games_played",
    "total_plays",
    "overall_performance",
    "overall_best_performance",
    "Memory",
    "Attention",
    "Reflex",
    "Perception",
    "Learning",
    "Reasoning"
]


# Keep only columns that actually exist
available_variables = [
    column
    for column in candidate_variables
    if column in analysis_df.columns
]


# ============================================================
# FORCE NUMERIC VALUES
# ============================================================

for column in available_variables:

    analysis_df[column] = pd.to_numeric(
        analysis_df[column],
        errors="coerce"
    )


print("\nVariables included in correlation analysis:")

for variable in available_variables:
    print(f"  - {variable}")


# ============================================================
# SPEARMAN CORRELATION
# ============================================================

n_variables = len(available_variables)

rho_matrix = pd.DataFrame(
    np.nan,
    index=available_variables,
    columns=available_variables
)

p_value_matrix = pd.DataFrame(
    np.nan,
    index=available_variables,
    columns=available_variables
)

n_matrix = pd.DataFrame(
    np.nan,
    index=available_variables,
    columns=available_variables
)


# ============================================================
# CALCULATE PAIRWISE CORRELATIONS
# ============================================================

long_results = []

for i, variable_x in enumerate(available_variables):

    for j, variable_y in enumerate(available_variables):

        x = analysis_df[variable_x]
        y = analysis_df[variable_y]

        # Pairwise complete observations
        pair = pd.concat(
            [x, y],
            axis=1
        ).dropna()

        x_clean = pair.iloc[:, 0].to_numpy()
        y_clean = pair.iloc[:, 1].to_numpy()

        n = len(pair)

        # Not enough observations
        if n < 3:

            rho = np.nan
            p_value = np.nan

        # Constant variable
        elif (
            np.unique(x_clean).size <= 1
            or np.unique(y_clean).size <= 1
        ):

            rho = np.nan
            p_value = np.nan

        else:

            result = spearmanr(
                x_clean,
                y_clean
            )

            # scipy normally returns scalar values here.
            # Explicit float conversion protects against
            # unexpected array-like results.
            rho = float(np.asarray(result.statistic).squeeze())
            p_value = float(np.asarray(result.pvalue).squeeze())

        rho_matrix.loc[
            variable_x,
            variable_y
        ] = rho

        p_value_matrix.loc[
            variable_x,
            variable_y
        ] = p_value

        n_matrix.loc[
            variable_x,
            variable_y
        ] = n

        long_results.append({
            "variable_1": variable_x,
            "variable_2": variable_y,
            "rho": rho,
            "p_value": p_value,
            "n": n
        })


# ============================================================
# SAVE CORRELATION MATRIX
# ============================================================

rho_matrix.to_csv(
    TABLES_DIR / "spearman_correlation_matrix.csv"
)

p_value_matrix.to_csv(
    TABLES_DIR / "spearman_p_values.csv"
)

n_matrix.to_csv(
    TABLES_DIR / "correlation_sample_sizes.csv"
)


# ============================================================
# SAVE LONG-FORM CORRELATIONS
# ============================================================

correlations_long = pd.DataFrame(
    long_results
)


# Remove self-correlations from the ranking table
ranking = correlations_long[
    correlations_long["variable_1"]
    != correlations_long["variable_2"]
].copy()


# Remove duplicate pairs
ranking["pair"] = ranking.apply(
    lambda row: tuple(
        sorted(
            [
                row["variable_1"],
                row["variable_2"]
            ]
        )
    ),
    axis=1
)

ranking = ranking.drop_duplicates(
    subset=["pair"]
)

ranking = ranking.drop(
    columns=["pair"]
)


# Sort by absolute correlation
ranking["absolute_rho"] = (
    ranking["rho"].abs()
)

ranking = ranking.sort_values(
    "absolute_rho",
    ascending=False,
    na_position="last"
)

ranking = ranking.drop(
    columns=["absolute_rho"]
)


ranking.to_csv(
    TABLES_DIR / "spearman_correlations_long.csv",
    index=False
)


# ============================================================
# CORRELATION HEATMAP
# ============================================================

plt.figure(
    figsize=(13, 10)
)

plt.imshow(
    rho_matrix.astype(float),
    aspect="auto"
)

plt.colorbar(
    label="Spearman rho"
)

plt.xticks(
    range(n_variables),
    available_variables,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(n_variables),
    available_variables
)

plt.title(
    "Spearman Correlation Matrix"
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "spearman_correlation_matrix.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# REPORT
# ============================================================

report_path = (
    REPORTS_DIR /
    "correlation_analysis.txt"
)


with open(
    report_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "SPEARMAN CORRELATION ANALYSIS\n"
    )

    f.write(
        "=" * 70 + "\n\n"
    )

    f.write(
        "Purpose\n"
    )

    f.write(
        "-------\n"
    )

    f.write(
        "This analysis examines exploratory associations "
        "between demographic/gameplay variables, overall "
        "performance, and cognitive-domain performance.\n\n"
    )

    f.write(
        "Variables\n"
    )

    f.write(
        "---------\n"
    )

    for variable in available_variables:

        f.write(
            f"- {variable}\n"
        )

    f.write("\n")

    f.write(
        "Important methodological notes\n"
    )

    f.write(
        "-------------------------------\n"
    )

    f.write(
        "- Spearman correlation is used because the sample "
        "is relatively small and relationships may not be "
        "normally distributed.\n"
    )

    f.write(
        "- Pairwise complete observations are used for each "
        "correlation.\n"
    )

    f.write(
        "- Correlations involving constant variables are "
        "reported as NaN because they are mathematically "
        "undefined.\n"
    )

    f.write(
        "- Correlation does not establish causation.\n"
    )

    f.write(
        "- Cognitive-domain assignments are based on the "
        "game design and should not be interpreted as "
        "clinically validated cognitive measurements.\n"
    )

    f.write("\n")

    f.write(
        "Strongest non-self correlations\n"
    )

    f.write(
        "--------------------------------\n"
    )

    valid_ranking = ranking.dropna(
        subset=["rho"]
    )

    for _, row in valid_ranking.head(15).iterrows():

        f.write(
            f"{row['variable_1']} <-> "
            f"{row['variable_2']}: "
            f"rho={row['rho']:.4f}, "
            f"p={row['p_value']:.4f}, "
            f"n={int(row['n'])}\n"
        )


# ============================================================
# SUMMARY
# ============================================================

valid_count = ranking["rho"].notna().sum()

undefined_count = ranking["rho"].isna().sum()


print("\n" + "=" * 60)
print("CORRELATION ANALYSIS COMPLETED")
print("=" * 60)

print(
    f"\nVariables analyzed: {n_variables}"
)

print(
    f"Valid pairwise correlations: {valid_count}"
)

print(
    f"Undefined correlations: {undefined_count}"
)

print(
    "\nGenerated files:"
)

print(
    TABLES_DIR /
    "spearman_correlation_matrix.csv"
)

print(
    TABLES_DIR /
    "spearman_p_values.csv"
)

print(
    TABLES_DIR /
    "correlation_sample_sizes.csv"
)

print(
    TABLES_DIR /
    "spearman_correlations_long.csv"
)

print(
    FIGURES_DIR /
    "spearman_correlation_matrix.png"
)

print(
    REPORTS_DIR /
    "correlation_analysis.txt"
)

print("\nDone.")