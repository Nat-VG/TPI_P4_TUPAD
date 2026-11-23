# Backend — Food Store

Natalia Gutiérrez. FastAPI + SQLModel.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Completar `SECRET_KEY` en `.env` y después:

```
python -m app.db.seed
uvicorn app.main:app --reload
```

Queda en http://localhost:8000 — docs en `/docs`.

Admin del seed: `admin` / `Admin1234!`
