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
print("COGNITIVE DOMAIN ANALYSIS")
print("=" * 60)

print(f"Records loaded: {len(df)}")


# ============================================================
# Extract cognitive domains
# ============================================================

df["cognitive_skills"] = (
    df["cognitive_skills"]
    .fillna("")
    .astype(str)
)

domain_df = df.assign(
    cognitive_domain=df["cognitive_skills"].str.split(";")
).explode("cognitive_domain")

domain_df["cognitive_domain"] = (
    domain_df["cognitive_domain"]
    .str.strip()
)

# Remove empty domains
domain_df = domain_df[
    domain_df["cognitive_domain"] != ""
].copy()


# ============================================================
# Domain-level analysis
# ============================================================

domain_analysis = (
    domain_df.groupby(
        "cognitive_domain",
        as_index=False
    )
    .agg(
        games=("game_id", "nunique"),

        participants=("player_id", "nunique"),

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
        )
    )
)


# ============================================================
# Convert to percentages
# ============================================================

domain_analysis["mean_average_percent"] = (
    domain_analysis["mean_average_score"] * 100
)

domain_analysis["median_average_percent"] = (
    domain_analysis["median_average_score"] * 100
)

domain_analysis["mean_best_percent"] = (
    domain_analysis["mean_best_score"] * 100
)

domain_analysis["median_best_percent"] = (
    domain_analysis["median_best_score"] * 100
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
    "mean_average_percent",
    "median_average_percent",
    "mean_best_percent",
    "median_best_percent"
]

for column in numeric_columns:
    domain_analysis[column] = (
        domain_analysis[column].round(4)
    )


# ============================================================
# Sort by domain name
# ============================================================

domain_analysis = domain_analysis.sort_values(
    "cognitive_domain"
)


# ============================================================
# Save table
# ============================================================

domain_analysis.to_csv(
    TABLES_DIR / "cognitive_domain_performance.csv",
    index=False
)


# ============================================================
# Domain-game detail
# ============================================================

domain_game_detail = (
    domain_df.groupby(
        [
            "cognitive_domain",
            "game_id",
            "game_title"
        ],
        as_index=False
    )
    .agg(
        participants=("player_id", "nunique"),

        mean_average_score=(
            "normalized_average_score",
            "mean"
        ),

        mean_best_score=(
            "normalized_best_score",
            "mean"
        ),

        total_plays=("play_count", "sum")
    )
)

domain_game_detail["mean_average_percent"] = (
    domain_game_detail["mean_average_score"] * 100
)

domain_game_detail["mean_best_percent"] = (
    domain_game_detail["mean_best_score"] * 100
)

domain_game_detail[
    [
        "mean_average_score",
        "mean_best_score",
        "mean_average_percent",
        "mean_best_percent"
    ]
] = domain_game_detail[
    [
        "mean_average_score",
        "mean_best_score",
        "mean_average_percent",
        "mean_best_percent"
    ]
].round(4)

domain_game_detail.to_csv(
    TABLES_DIR / "cognitive_domain_game_detail.csv",
    index=False
)


# ============================================================
# Figure 1: Average performance by cognitive domain
# ============================================================

plot_data = domain_analysis.sort_values(
    "mean_average_percent",
    ascending=True
)

plt.figure(figsize=(9, 6))

plt.barh(
    plot_data["cognitive_domain"],
    plot_data["mean_average_percent"]
)

plt.xlabel("Mean Average Performance (%)")
plt.ylabel("Cognitive Domain")
plt.title("Performance by Cognitive Domain")
plt.xlim(0, 100)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "cognitive_domain_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Figure 2: Best vs average by cognitive domain
# ============================================================

plot_data = domain_analysis.sort_values(
    "cognitive_domain"
)

x = range(len(plot_data))

plt.figure(figsize=(10, 6))

plt.plot(
    x,
    plot_data["mean_average_percent"],
    marker="o",
    label="Mean Average Score"
)

plt.plot(
    x,
    plot_data["mean_best_percent"],
    marker="o",
    label="Mean Best Score"
)

plt.xticks(
    list(x),
    plot_data["cognitive_domain"],
    rotation=30
)

plt.ylabel("Performance (%)")
plt.xlabel("Cognitive Domain")
plt.title("Average vs Best Performance by Cognitive Domain")
plt.ylim(0, 100)
plt.legend()

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "cognitive_domain_best_vs_average.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Report
# ============================================================

report_path = REPORTS_DIR / "cognitive_domain_analysis.txt"

with open(report_path, "w", encoding="utf-8") as f:

    f.write("COGNITIVE DOMAIN ANALYSIS REPORT\n")
    f.write("=" * 60 + "\n\n")

    f.write(
        "Games may belong to multiple cognitive domains. "
        "Therefore, a game contributes to every domain assigned "
        "to that game.\n\n"
    )

    f.write("Domain-level results:\n")
    f.write("-" * 60 + "\n")

    for _, row in domain_analysis.iterrows():

        f.write(
            f"{row['cognitive_domain']:<15} | "
            f"Games: {row['games']:>2} | "
            f"Participants: {row['participants']:>3} | "
            f"Mean Performance: "
            f"{row['mean_average_percent']:.2f}% | "
            f"Mean Best: "
            f"{row['mean_best_percent']:.2f}%\n"
        )


print("\nCognitive domain analysis completed.")
print(
    f"Table: "
    f"{TABLES_DIR / 'cognitive_domain_performance.csv'}"
)
print(f"Figures: {FIGURES_DIR}")
print(f"Report: {report_path}")