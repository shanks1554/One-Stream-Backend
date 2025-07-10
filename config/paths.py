from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # No change if config is inside /config

class P:
    ROOT = ROOT
    CONFIG = ROOT / "config"
    DATA = ROOT / "data"
    DATA_PROCESSED = DATA / "processed"

    # Data files
    CLEAN_ANIME_CSV = DATA_PROCESSED / "clean_anime.csv"
    ANIME_DATASET_CSV = DATA / "anime_dataset.csv"
    ANIME_FEATURES_FILE = DATA_PROCESSED / "anime_features.csv"
