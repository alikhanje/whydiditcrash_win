import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5433,
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id SERIAL PRIMARY KEY,
                occurred_at TIMESTAMPTZ NOT NULL UNIQUE,
                type TEXT NOT NULL,
                stop_code INTEGER,
                stop_name TEXT
            )
            """
        )


def save_incident(occurred_at, incident_type, stop_code=None, stop_name=None):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO incidents (occurred_at, type, stop_code, stop_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (occurred_at) DO NOTHING
            """,
            (occurred_at, incident_type, stop_code, stop_name),
        )