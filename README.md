# Service Desk

## Student

- Name: ศุภกร สิริเกื้อกูลชัย
- Student ID: 6706022510174

## Technology

- Python 3.12
- FastAPI 0.115.12
- Uvicorn 0.34.0
- SQLite (Python standard library)
- Nginx 1.27 Alpine
- Docker Compose
- HTML, CSS, and vanilla JavaScript

## Project structure

```text
.
├── backend/
│   ├── app/main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.js
│   ├── index.html
│   ├── nginx.conf
│   ├── Dockerfile
│   └── styles.css
└── compose.yaml
```

## Run locally with Docker

Docker Engine and the Docker Compose plugin are the only host requirements.

```powershell
docker compose up --build -d
docker compose ps
```

Open the application at [http://localhost:8080](http://localhost:8080). The browser uses `API_BASE = "/api"`; Nginx forwards API requests to the backend container.

Stop the containers without removing saved tickets:

```powershell
docker compose down
docker compose up -d
```

To rebuild after changing the application, run `docker compose up --build -d`.

## API

- `GET /api/health`
- `GET /api/tickets`
- `POST /api/tickets` with `{"title":"Printer offline","priority":"high"}`
- `PATCH /api/tickets/{id}` with `{"status":"doing"}`

The API validates and trims ticket titles. New tickets always start with `open`; status can be changed freely among `open`, `doing`, and `done`.

## Data persistence

The Compose named volume `service_desk_data` is mounted into the backend container at `/data`. SQLite stores tickets in `/data/tickets.db`. `docker compose down` preserves this volume; `docker compose down -v` removes it and its data.
