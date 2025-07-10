
# 🎯 One Stream Backend - Anime Recommendation System

This is the backend API for **One Stream**, an Anime Recommendation System. It is built using **FastAPI** and serves recommendations based on anime titles and genres.

---

## 🚀 Features

- Recommend anime by watched list
- Explore top anime by genre
- Autocomplete anime titles
- Get detailed anime metadata
- CORS enabled for frontend communication

---

## 📁 Project Structure

```
One-Stream-Backend/
├── main.py              # FastAPI application entrypoint
├── meta.py              # Metadata loader and genre filter logic
├── recommend.py         # Core recommendation logic
├── config/
│   └── paths.py         # Central path manager for files
├── data/
│   └── processed/
│       ├── clean_anime.csv
│       └── anime_features.csv
│   └── anime_dataset.csv
└── requirements.txt     # Python dependencies
```

---

## 📡 API Endpoints

| Method | Endpoint        | Description                          |
|--------|------------------|--------------------------------------|
| GET    | `/`              | Health check root                    |
| GET    | `/ping`          | Ping server                          |
| GET    | `/meta`          | Get anime metadata by title          |
| GET    | `/poster`        | Get poster URL by title              |
| POST   | `/recommend`     | Recommend anime by liked titles      |
| POST   | `/genres`        | Get top anime by selected genres     |
| GET    | `/autocomplete`  | Autocomplete titles by prefix        |

---

## 📦 Installation

```bash
# Create a virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Run Locally

```bash
# From project root
uvicorn main:app --reload
```

---

## 🌐 CORS Configuration

CORS is configured to allow all origins (development use).  
To restrict origins in production, modify:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace * with your frontend domain in prod
    ...
)
```

---

## 🛠 Dependencies

See `requirements.txt` for the full list.

---

## 📜 License

MIT License - Free to use and modify.

---

## 🙌 Author

Made with ❤️ by Deep Nagpal
