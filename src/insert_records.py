import psycopg2
import os
from test import mock_fetch_data

def connect_to_db():
    print("Connecting to the PostgreSQL database...")
    try:
        conn = psycopg2.connect(
            host     = "127.0.0.1",
            port     = 5432,
            dbname   = "db",
            user     = "db_user",
            password = "db_password"
            # connect_timeout = 5,            # optional: fail fast if wrong
        )
        print(conn)
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        raise 

connect_to_db()