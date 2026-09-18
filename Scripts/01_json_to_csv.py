import json
import csv
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_JSON_DIR = PROJECT_ROOT / "data" / "raw_json"

PLAYERS_CSV = PROJECT_ROOT / "data" / "players.csv"
GAME_SCORES_CSV = PROJECT_ROOT / "data" / "game_scores.csv"
GAME_METADATA_CSV = PROJECT_ROOT / "data" / "game_metadata.csv"


# ============================================================
# GAME METADATA
# ============================================================

GAME_METADATA = {
    0: {
        "game_title": "Cipher Rush",
        "game_type": "minigame",
        "cognitive_skills": "Attention;Reflex",
        "max_score": 250,
    },
    1: {
        "game_title": "Match-a-Mole",
        "game_type": "minigame",
        "cognitive_skills": "Reflex;Attention",
        "max_score": 300,
    },
    2: {
        "game_title": "Good Guy, Bad Guy",
        "game_type": "minigame",
        "cognitive_skills": "Memory",
        "max_score": 200,
    },
    3: {
        "game_title": "Feed The Fishes",
        "game_type": "minigame",
        "cognitive_skills": "Memory;Attention",
        "max_score": 90,
    },
    4: {
        "game_title": "Train of Thoughts",
        "game_type": "minigame",
        "cognitive_skills": "Reflex;Reasoning",
        "max_score": 200,
    },
    5: {
        "game_title": "Match The Notes",
        "game_type": "minigame",
        "cognitive_skills": "Memory;Perception",
        "max_score": 200,
    },
    6: {
        "game_title": "Wordify",
        "game_type": "minigame",
        "cognitive_skills": "Learning",
        "max_score": 70,
    },
    7: {
        "game_title": "Find Me If You Can",
        "game_type": "minigame",
        "cognitive_skills": "Perception",
        "max_score": 275,
    },
    8: {
        "game_title": "Word Reveal",
        "game_type": "minigame",
        "cognitive_skills": "Attention;Memory",
        "max_score": 170,
    },
    9: {
        "game_title": "Precision Product",
        "game_type": "minigame",
        "cognitive_skills": "Reflex;Learning",
        "max_score": 225,
    },
    10: {
        "game_title": "Sequence Grid",
        "game_type": "minigame",
        "cognitive_skills": "Memory",
        "max_score": 100,
    },
    11: {
        "game_title": "Perception Match",
        "game_type": "minigame",
        "cognitive_skills": "Perception;Memory",
        "max_score": 250,
    },
    12: {
        "game_title": "Faster, Please",
        "game_type": "minigame",
        "cognitive_skills": "Reflex",
        "max_score": 200,
    },
    13: {
        "game_title": "Wordle",
        "game_type": "minigame",
        "cognitive_skills": "Learning;Reasoning",
        "max_score": 170,
    },
    14: {
        "game_title": "Word Bubble",
        "game_type": "minigame",
        "cognitive_skills": "Learning",
        "max_score": 200,
    },
    15: {
        "game_title": "Sequence Match",
        "game_type": "minigame",
        "cognitive_skills": "Memory",
        "max_score": 80,
    },
    16: {
        "game_title": "Verbal Memory",
        "game_type": "minigame",
        "cognitive_skills": "Memory",
        "max_score": 250,
    },
    17: {
        "game_title": "Number Memory",
        "game_type": "minigame",
        "cognitive_skills": "Memory",
        "max_score": 125,
    },
    18: {
        "game_title": "Stop The Clock",
        "game_type": "minigame",
        "cognitive_skills": "Reflex",
        "max_score": 800,
    },
    19: {
        "game_title": "Odd One Out",
        "game_type": "minigame",
        "cognitive_skills": "Reasoning",
        "max_score": 175,
    },

    # Core five levels
    30: {
        "game_title": "Level 1",
        "game_type": "level",
        "cognitive_skills": "Reflex;Attention",
        "max_score": 95,
    },
    31: {
        "game_title": "Level 2",
        "game_type": "level",
        "cognitive_skills": "Memory;Attention",
        "max_score": 100,
    },
    32: {
        "game_title": "Level 3",
        "game_type": "level",
        "cognitive_skills": "Memory;Perception",
        "max_score": 85,
    },
    33: {
        "game_title": "Level 4",
        "game_type": "level",
        "cognitive_skills": "Reasoning;Reflex",
        "max_score": 120,
    },
    34: {
        "game_title": "Level 5",
        "game_type": "level",
        "cognitive_skills": "Reasoning",
        "max_score": 190,
    },
}


# ============================================================
# CSV WRITER
# ============================================================

def write_csv(file_path, fieldnames, rows):
    """
    Write a list of dictionaries to a CSV file.
    """

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# GAME METADATA CSV
# ============================================================

def create_game_metadata_csv():
    """
    Create game_metadata.csv containing information about
    all 25 cognitive games.
    """

    rows = []

    for game_id in sorted(GAME_METADATA.keys()):

        game = GAME_METADATA[game_id]

        rows.append({
            "game_id": game_id,
            "game_title": game["game_title"],
            "game_type": game["game_type"],
            "cognitive_skills": game["cognitive_skills"],
            "max_score": game["max_score"],
        })

    fields = [
        "game_id",
        "game_title",
        "game_type",
        "cognitive_skills",
        "max_score",
    ]

    write_csv(
        GAME_METADATA_CSV,
        fields,
        rows
    )


# ============================================================
# JSON → CSV CONVERSION
# ============================================================

def convert_json_files():

    player_rows = []
    game_rows = []

    json_files = sorted(
        RAW_JSON_DIR.glob("player_*.json")
    )

    if not json_files:
        print("ERROR: No player JSON files found.")
        print(f"Expected files inside: {RAW_JSON_DIR}")
        return

    print(f"Found {len(json_files)} JSON file(s).\n")

    for json_file in json_files:

        # ----------------------------------------------------
        # Player ID
        # ----------------------------------------------------

        # Example:
        # player_36f8a2f6.json
        #
        # becomes:
        # 36f8a2f6

        filename = json_file.stem

        player_id = filename.replace(
            "player_",
            "",
            1
        )

        # ----------------------------------------------------
        # Read JSON
        # ----------------------------------------------------

        try:

            with open(
                json_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except json.JSONDecodeError as error:

            print(
                f"ERROR: Invalid JSON in "
                f"{json_file.name}"
            )

            print(error)
            continue

        # ----------------------------------------------------
        # Player information
        # ----------------------------------------------------

        player_rows.append({
            "player_id": player_id,
            "age": data.get("age"),
            "gender": data.get("gender"),
            "country": data.get("country"),
            "favorite_genre": data.get("favoriteGenre"),
            "weekly_gaming_hours": data.get(
                "weeklyGamingHours"
            ),
            "sleep_hours_last_night": data.get(
                "sleepHoursLastNight"
            ),
        })

        # ----------------------------------------------------
        # Game statistics
        # ----------------------------------------------------

        game_stats = data.get(
            "gameStats",
            []
        )

        recognized_games = 0

        for game in game_stats:

            game_id = game.get("gameId")

            # Ignore unknown game IDs
            if game_id not in GAME_METADATA:

                print(
                    f"WARNING: Unknown game ID "
                    f"{game_id} in {json_file.name}"
                )

                continue

            metadata = GAME_METADATA[game_id]

            game_rows.append({
                "player_id": player_id,

                "game_id": game_id,

                "game_title": metadata[
                    "game_title"
                ],

                "game_type": metadata[
                    "game_type"
                ],

                "cognitive_skills": metadata[
                    "cognitive_skills"
                ],

                "max_score": metadata[
                    "max_score"
                ],

                "raw_best_score": game.get(
                    "bestScore"
                ),

                "raw_average_score": game.get(
                    "averageScore"
                ),

                "play_count": game.get(
                    "playCount"
                ),
            })

            recognized_games += 1

        print(
            f"{json_file.name}: "
            f"{recognized_games} game record(s)"
        )

    # ========================================================
    # WRITE PLAYERS CSV
    # ========================================================

    player_fields = [
        "player_id",
        "age",
        "gender",
        "country",
        "favorite_genre",
        "weekly_gaming_hours",
        "sleep_hours_last_night",
    ]

    write_csv(
        PLAYERS_CSV,
        player_fields,
        player_rows
    )

    # ========================================================
    # WRITE GAME SCORES CSV
    # ========================================================

    game_fields = [
        "player_id",
        "game_id",
        "game_title",
        "game_type",
        "cognitive_skills",
        "max_score",
        "raw_best_score",
        "raw_average_score",
        "play_count",
    ]

    write_csv(
        GAME_SCORES_CSV,
        game_fields,
        game_rows
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("JSON → CSV CONVERSION COMPLETE")
    print("=" * 60)

    print(f"\nPlayers found: {len(player_rows)}")
    print(f"Game records:  {len(game_rows)}")

    print("\nCreated files:")

    print(f"  {PLAYERS_CSV}")
    print(f"  {GAME_SCORES_CSV}")
    print(f"  {GAME_METADATA_CSV}")

    print("\nNo cleaning or normalization was performed.")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MindGrind Data Converter")
    print("=" * 60)

    if not RAW_JSON_DIR.exists():

        print(
            f"\nERROR: Raw JSON directory does not exist:\n"
            f"{RAW_JSON_DIR}"
        )

        return

    create_game_metadata_csv()

    convert_json_files()


if __name__ == "__main__":
    main()