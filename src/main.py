import asyncio
from datetime import date, datetime
from typing import Callable, List

import uvicorn
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pytz import timezone

from . import db
from .scraping import a38, bem, tixa

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")

templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> Response:
    with db.create_con() as con:
        events = db.get_events(con)
        types = db.get_types(con)
        addresses = db.get_addresses(con)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"events": events, "types": types, "addresses": addresses},
        )


@app.get("/events", response_class=HTMLResponse)
def events(
    request: Request,
    from_date: str | None = None,
    to_date: str | None = None,
    addresses: List[str] | None = Query(None),
    types: List[str] | None = Query(None),
) -> Response:
    with db.create_con() as con:
        events = db.get_events(con)

        # TODO: Return 400 Bad Request if the date is not an ISO date
        if from_date is not None and from_date != "":
            from_date_parsed = date.fromisoformat(from_date)
            from_datetime = datetime.combine(
                from_date_parsed, datetime.min.time(), timezone("Europe/Budapest")
            )
            events = [
                event for event in events if event.start_datetime >= from_datetime
            ]

        if to_date is not None and to_date != "":
            to_date_parsed = date.fromisoformat(to_date)
            to_datetime = datetime.combine(
                to_date_parsed, datetime.max.time(), timezone("Europe/Budapest")
            )
            events = [event for event in events if event.start_datetime <= to_datetime]

        if (
            addresses is not None
            and len(addresses) > 0
            and "everything" not in addresses
        ):
            events = [event for event in events if event.address in addresses]

        if types is not None and len(types) > 0 and "everything" not in types:
            events = [event for event in events if event.type in types]

        return templates.TemplateResponse(
            request=request, name="fragments/events.html", context={"events": events}
        )


@app.get("/refresh")
async def refresh() -> str:
    with db.create_con() as con:
        con.execute("DROP TABLE IF EXISTS events")
        db.create_table(con)

        scapers = [
            a38.get_a38_concerts,
            bem.get_bem_movies,
            tixa.get_budapest_park_concerts,
            tixa.get_durer_kert_concerts,
            tixa.get_turbina_concerts,
        ]

        async def run_async(f: Callable) -> None:
            print(f"Running scaper {f.__name__}")
            events = f()
            db.write_to_db(con, events)
            print(
                f"Finished running scaper {f.__name__} and finished writing into the DB"
            )

        # TODO: This doesn't seem to execute in async
        await asyncio.gather(*[run_async(f) for f in scapers])

    return "OK"


if __name__ == "__main__":
    con = db.create_con()
    db.create_table(con)
    con.close()

    uvicorn.run(app, host="0.0.0.0", port=8000)
