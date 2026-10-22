import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StrictStr, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
DATABASE_PATH = DATA_DIR / "tickets.db"

Priority = Literal["low", "medium", "high"]
Status = Literal["open", "doing", "done"]

app = FastAPI(title="Service Desk API")


class CreateTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: StrictStr
    priority: Priority

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not 1 <= len(value) <= 80:
            raise ValueError("title must be between 1 and 80 characters after trimming")
        return value


class UpdateTicketStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Status


class Ticket(BaseModel):
    id: int
    title: str
    priority: Priority
    status: Status


def connect_database() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with closing(connect_database()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 80),
                priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high')),
                status TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open', 'doing', 'done'))
            )
            """
        )
        connection.commit()


def serialize_ticket(row: sqlite3.Row) -> Ticket:
    return Ticket(
        id=row["id"],
        title=row["title"],
        priority=row["priority"],
        status=row["status"],
    )


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    del request
    first_error = exc.errors()[0]
    location = ".".join(str(part) for part in first_error["loc"])
    return JSONResponse(
        status_code=422,
        content={"error": f"{location}: {first_error['msg']}"},
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    del request
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(status_code=exc.status_code, content={"error": message})


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tickets", response_model=list[Ticket])
def list_tickets() -> list[Ticket]:
    with closing(connect_database()) as connection:
        rows = connection.execute(
            "SELECT id, title, priority, status FROM tickets ORDER BY id"
        ).fetchall()
    return [serialize_ticket(row) for row in rows]


@app.post("/api/tickets", response_model=Ticket, status_code=201)
def create_ticket(ticket: CreateTicket) -> Ticket:
    with closing(connect_database()) as connection:
        cursor = connection.execute(
            "INSERT INTO tickets (title, priority) VALUES (?, ?)",
            (ticket.title, ticket.priority),
        )
        connection.commit()
        row = connection.execute(
            "SELECT id, title, priority, status FROM tickets WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return serialize_ticket(row)


@app.patch("/api/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: int, update: UpdateTicketStatus) -> Ticket:
    with closing(connect_database()) as connection:
        cursor = connection.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (update.status, ticket_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
        row = connection.execute(
            "SELECT id, title, priority, status FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()
    return serialize_ticket(row)
