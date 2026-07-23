import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def load_json(filename: str) -> list[dict]:
    """Charge un fichier JSON."""

    file_path = RAW_DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Le fichier {file_path} est introuvable. "
            "Exécute d'abord extract.py."
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_movies_table(movies_data: list[dict]) -> pd.DataFrame:
    """Crée la table principale des films."""

    rows = []

    for movie in movies_data:
        release_date = movie.get("release_date") or None

        rows.append(
            {
                "movie_id": movie.get("id"),
                "title": movie.get("title"),
                "original_title": movie.get("original_title"),
                "release_date": release_date,
                "original_language": movie.get("original_language"),
                "popularity": movie.get("popularity"),
                "vote_average": movie.get("vote_average"),
                "vote_count": movie.get("vote_count"),
                "adult": movie.get("adult"),
            }
        )

    dataframe = pd.DataFrame(rows)

    dataframe["release_date"] = pd.to_datetime(
        dataframe["release_date"],
        errors="coerce",
    )

    dataframe["release_year"] = dataframe["release_date"].dt.year

    dataframe = dataframe.drop_duplicates(subset=["movie_id"])

    return dataframe


def create_genres_table(genres_data: list[dict]) -> pd.DataFrame:
    """Crée la table des genres."""

    dataframe = pd.DataFrame(genres_data)

    dataframe = dataframe.rename(
        columns={
            "id": "genre_id",
            "name": "genre_name",
        }
    )

    return dataframe[["genre_id", "genre_name"]]


def create_movie_genres_table(
    movies_data: list[dict],
) -> pd.DataFrame:
    """Crée la table de liaison entre les films et les genres."""

    rows = []

    for movie in movies_data:
        movie_id = movie.get("id")
        genre_ids = movie.get("genre_ids", [])

        for genre_id in genre_ids:
            rows.append(
                {
                    "movie_id": movie_id,
                    "genre_id": genre_id,
                }
            )

    dataframe = pd.DataFrame(rows)
    dataframe = dataframe.drop_duplicates()

    return dataframe


def save_csv(dataframe: pd.DataFrame, filename: str) -> None:
    """Enregistre un DataFrame dans un fichier CSV."""

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = PROCESSED_DATA_DIR / filename

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Fichier créé : {output_path}")
    print(f"Nombre de lignes : {len(dataframe)}")


def main() -> None:
    movies_data = load_json("movies_raw.json")
    genres_data = load_json("genres_raw.json")

    movies_table = create_movies_table(movies_data)
    genres_table = create_genres_table(genres_data)
    movie_genres_table = create_movie_genres_table(movies_data)

    save_csv(movies_table, "movies.csv")
    save_csv(genres_table, "genres.csv")
    save_csv(movie_genres_table, "movie_genres.csv")


if __name__ == "__main__":
    main()