from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Type


@dataclass
class EventInfo:
    type: str
    url: str
    name: str
    start_datetime: datetime
    address: str

    @classmethod
    def from_row(cls: Type[EventInfo], row: sqlite3.Row) -> EventInfo:
        return cls(
            type=row["type"],
            url=row["url"],
            name=row["name"],
            start_datetime=datetime.fromisoformat(row["start_datetime"]),
            address=row["address"],
        )


def create_con() -> sqlite3.Connection:
    con = sqlite3.connect("test.db")
    con.row_factory = sqlite3.Row
    return con


def create_table(con: sqlite3.Connection) -> None:
    con.execute(
        "CREATE TABLE IF NOT EXISTS events(type, url, name, start_datetime, address)"
    )
    con.commit()


def write_to_db(con: sqlite3.Connection, events: List[EventInfo]) -> None:
    con.executemany(
        "INSERT INTO events VALUES(?, ?, ?, ?, ?)",
        map(
            lambda x: (x.type, x.url, x.name, x.start_datetime.isoformat(), x.address),
            events,
        ),
    )
    con.commit()


def get_events(con: sqlite3.Connection) -> List[EventInfo]:
    return [
        EventInfo.from_row(row)
        for row in con.execute("SELECT * FROM events ORDER BY start_datetime")
    ]


def get_types(con: sqlite3.Connection) -> List[str]:
    return [
        row["type"]
        for row in con.execute("SELECT DISTINCT type FROM events ORDER BY type")
    ]


def get_addresses(con: sqlite3.Connection) -> List[str]:
    return [
        row["address"]
        for row in con.execute("SELECT DISTINCT address FROM events ORDER BY address")
    ]
