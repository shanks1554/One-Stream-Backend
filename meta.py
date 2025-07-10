# backend/meta.py
import pandas as pd
from functools import lru_cache
from config.paths import P
CLEAN_CSV = P.CLEAN_ANIME_CSV

@lru_cache(maxsize=1)
def _load():
    print("Loading CSV from:", CLEAN_CSV)
    if not CLEAN_CSV.exists():
        print("❌ clean_anime.csv NOT FOUND at", CLEAN_CSV)
        return None
    
    df = pd.read_csv(CLEAN_CSV)
    df["title_lower"] = df["Title"].str.lower()
    return df    
def get_meta(title: str) -> dict | None:
    df = _load()
    row = df[df['title_lower'] == title.lower()]
    if row.empty:
        return None
    r = row.iloc[0]
    return {
        "title": r["Title"],
        "score": r["Score"],
        "episodes": r["Episodes"],
        "poster": r["Image URL"],
        "synopsis": r["Synopsis"],
        "studios": r["Studios"],
        "popularity": r["Popularity"],
        "ranked": r["Ranked"],
    }
    
def top_by_genres(genres: list[str], k: int = 10) -> list[dict]:
    """
    Return top‑k anime (dict) that contain *all* given genres,
    ranked by Score descending.
    """
    df = _load()
    # Build column names: our one‑hot columns are lower‑case genre names
    gcols = [g.strip().lower() for g in genres]
    missing = [g for g in gcols if g not in df.columns]
    if missing:
        raise ValueError(f"Unknown genres: {', '.join(missing)}")

    mask = df[gcols].all(axis=1)          # ALL genres (AND)
    subset = df[mask].sort_values("Score", ascending=False).head(k)

    records = []
    for _, row in subset.iterrows():
        records.append({
            "title": row["Title"],
            "score": row["Score"],
            "poster": row["Image URL"],
            "synopsis": row["Synopsis"],
            "similarity": None   # not relevant here
        })
    return records