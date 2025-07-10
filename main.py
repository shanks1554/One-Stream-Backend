# backend/main.py
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from recommend import recommend_from_titles
from meta import get_meta, top_by_genres
from config.paths import P

# ----------------------------------------------------------
# Data loading for lightweight endpoints (/meta, /poster, /autocomplete)
# ----------------------------------------------------------
ANIME_META = pd.read_csv(P.CLEAN_ANIME_CSV)
ANIME_META["title_lower"] = ANIME_META["Title"].fillna("").str.lower()

# ----------------------------------------------------------
# FastAPI init + CORS
# ----------------------------------------------------------
app = FastAPI(
    title="OneStream Anime Recommender",
    description="Recommend anime based on watched titles and genres.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],               # for local dev; tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# Request schemas
# ----------------------------------------------------------
class GenreRequest(BaseModel):
    genres: List[str] = Field(..., examples=["Action", "Comedy"])
    k: int = Field(10, ge=1, le=20)


class RecommendRequest(BaseModel):
    liked_titles: List[str]
    genre_filter: Optional[List[str]] = None
    top_n: int = 10


# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------
@app.get("/")
def root():
    return {"message": "One Stream working correctly"}


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/recommend")
def recommend_route(body: RecommendRequest):
    try:
        rec_df = recommend_from_titles(
            liked_titles=body.liked_titles,
            k=body.top_n,
            genre_filter=body.genre_filter,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return rec_df.to_dict(orient="records")


@app.get("/meta")
def meta_route(title: str = Query(..., min_length=2)):
    data = get_meta(title)
    if data is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return data


@app.get("/poster")
def poster_route(title: str = Query(..., min_length=2)):
    data = get_meta(title)
    if data is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return {"title": data["title"], "poster": data["poster"]}


@app.post("/genres")
def genre_route(body: GenreRequest):
    try:
        result = top_by_genres(body.genres, k=body.k)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not result:
        raise HTTPException(status_code=404, detail="No anime found for those genres")

    return result


@app.get("/autocomplete")
def autocomplete_route(
    prefix: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
):
    prefix_lc = prefix.lower().strip()
    safe_df = ANIME_META.dropna(subset=["title_lower"])
    matches = safe_df[safe_df["title_lower"].str.startswith(prefix_lc)].head(limit)

    return [
        {
            "title": row["Title"],
            "poster_url": row.get("Image URL", ""),
        }
        for _, row in matches.iterrows()
    ]
