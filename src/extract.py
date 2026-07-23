import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


# Racine du projet : tmdb-movie-analytics/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

BASE_URL = "https://api.themoviedb.org/3"

load_dotenv(PROJECT_ROOT / ".env")

TMDB_TOKEN = os.getenv("TMDB_TOKEN")

if not TMDB_TOKEN:
    raise ValueError(
        "Le token TMDB est absent. "
        "Ajoute TMDB_TOKEN dans le fichier .env."
    )

HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json",
}


def request_tmdb(endpoint: str, params: dict | None = None) -> dict:
    """Envoie une requête GET à l'API TMDB."""

    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=HEADERS,
        params=params,
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def extract_movies(number_of_pages: int = 10) -> list[dict]:
    """Récupère plusieurs pages de films populaires."""

    movies = []

    for page in range(1, number_of_pages + 1):
        print(f"Récupération de la page {page}/{number_of_pages}")

        data = request_tmdb(
            endpoint="/discover/movie",
            params={
                "language": "fr-FR",
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "page": page,
            },
        )

        movies.extend(data.get("results", []))

        # Petite pause pour éviter d'enchaîner les requêtes trop vite.
        time.sleep(0.2)

    return movies


def extract_genres() -> list[dict]:
    """Récupère la liste officielle des genres de films."""

    data = request_tmdb(
        endpoint="/genre/movie/list",
        params={"language": "fr-FR"},
    )

    return data.get("genres", [])


def save_json(data: list[dict], filename: str) -> None:
    """Enregistre des données dans un fichier JSON."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DATA_DIR / filename

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"Fichier créé : {output_path}")


def main() -> None:
    movies = extract_movies(number_of_pages=10)
    genres = extract_genres()

    save_json(movies, "movies_raw.json")
    save_json(genres, "genres_raw.json")

    print(f"{len(movies)} films récupérés.")
    print(f"{len(genres)} genres récupérés.")


if __name__ == "__main__":
    main()

    