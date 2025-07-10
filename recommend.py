# backend/recommend.py
from functools import lru_cache
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize

from config.paths import P

# ----------------------------------------------------------
# File locations
# ----------------------------------------------------------
FEAT_CSV  = P.ANIME_FEATURES_FILE      # models/anime_features.csv
META_CSV  = P.CLEAN_ANIME_CSV          # data/animated/clean_anime.csv

# ----------------------------------------------------------
# Lazy loaders
# ----------------------------------------------------------
@lru_cache(maxsize=1)
def _load_features():
    """Return (df, matrix, vector_cols, title→idx)."""
    df = pd.read_csv(FEAT_CSV)

    # Ensure title column is lowercase "title"
    if "title" not in df.columns:
        df = df.rename(columns={"Title": "title"})

    vec_cols = df.columns.difference(["title", "poster", "Image URL", "MAL_ID"])
    mat = normalize(df[vec_cols].astype(float).values, axis=1)

    title_to_idx = {
        t.lower(): i
        for i, t in enumerate(df["title"].fillna(""))
        if t.strip()
    }
    return df, mat, vec_cols, title_to_idx


@lru_cache(maxsize=1)
def _load_meta():
    """Map lower‑case title → poster url (from clean CSV)."""
    meta = pd.read_csv(META_CSV)[["Title", "Image URL"]]
    return {
        t.lower(): url
        for t, url in zip(meta["Title"].fillna(""), meta["Image URL"].fillna(""))
        if t.strip()
    }


# ----------------------------------------------------------
# Public API
# ----------------------------------------------------------
def recommend_from_titles(
    liked_titles: List[str],
    k: int = 10,
    genre_filter: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Returns DataFrame with columns: title, poster, score
    """
    df, mat, vec_cols, title_to_idx = _load_features()
    poster_map = _load_meta()

    idxs = [title_to_idx.get(t.lower().strip()) for t in liked_titles]
    valid_idxs = [i for i in idxs if i is not None]
    if not valid_idxs:
        raise ValueError("None of the provided titles matched the catalogue.")

    user_vec = normalize(mat[valid_idxs].sum(axis=0, keepdims=True), axis=1)
    scores = (user_vec @ mat.T).ravel()
    scores[valid_idxs] = -1.0

    # Optional genre mask
    if genre_filter:
        gcols = [f"genre_{g.strip().title()}" for g in genre_filter]
        gcols = [c for c in gcols if c in vec_cols]
        if gcols:
            mask = df[gcols].sum(axis=1) > 0
            scores = np.where(mask, scores, -1.0)

    best_idx = scores.argsort()[-k:][::-1]

    # Determine poster source
    if "poster" in df.columns:
        poster_series = df["poster"]
    elif "Image URL" in df.columns:
        poster_series = df["Image URL"]
    else:
        poster_series = df["title"].str.lower().map(poster_map).fillna("")

    out = (
        df.loc[best_idx, ["title"]]
        .assign(
            poster=poster_series.iloc[best_idx].values,
            score=scores[best_idx].round(4),
        )
        .reset_index(drop=True)
    )
    return out

