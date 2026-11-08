from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Generator, Optional

import pyodbc


def connect_database(conn_str: Optional[str] = None) -> Any:
    """Connect to the Patika SQL Server database."""
    connection_string = conn_str or os.getenv("PATIKA_DB_CONNECTION_STRING")
    if not connection_string:
        # A te beállításaid fixen megadva:
        driver = "ODBC Driver 18 for SQL Server"
        server = "tcp:patikaprojekt2.database.windows.net"
        database = "patikaDB"
        user = "ssadmin"
        password = "Patika2026"

        parts = [
            f"Driver={{{driver}}}",
            f"Server={server},1433",      # <-- Hozzáadtuk a portot
            f"Database={database}",
            f"UID={user}",
            f"PWD={password}",
            "Encrypt=yes",                # <-- Kötelező az Azure felhőhöz
            "TrustServerCertificate=yes"   # <-- Biztonságos tanúsítványkezelés
        ]

        connection_string = ";".join(parts) + ";"

    return pyodbc.connect(connection_string)



@contextmanager
def database_connection(conn_str: Optional[str] = None) -> Generator[Any, None, None]:
    connection = connect_database(conn_str)
    try:
        with connection:
            yield connection
    finally:
        connection.close()
