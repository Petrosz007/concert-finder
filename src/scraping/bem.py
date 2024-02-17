from __future__ import annotations

from datetime import datetime
from typing import List

import parsel
import requests
from pytz import timezone

from src.db import EventInfo


def get_bem_movies() -> List[EventInfo]:
    html_data = requests.get("https://cooltix.hu/b/bemmozi").text

    selector = parsel.Selector(text=html_data)

    movies = []
    for event in selector.css("main div a"):
        # If this is true, then these elements are Movie Passes, we want to skip them
        if event.xpath(".//article/div[2]/div[2]").get() is None:
            continue

        path = event.xpath(".//@href").get()
        name = event.xpath(".//article/div[2]/div[2]/h3/text()").get()
        start_raw = event.xpath(".//article/div[2]/div[2]/div[1]/text()").get()
        address = event.xpath(".//article/div[2]/div[2]/div[3]/text()").get()

        if (
            path is not None
            and start_raw is not None
            and address is not None
            and name is not None
        ):
            parsed_start_datetime = datetime.strptime(
                f"{datetime.now().year} {start_raw}", "%Y %A, %b %d, %I:%M %p"
            ).replace(tzinfo=timezone("Europe/Budapest"))
            url = "https://cooltix.hu" + path
            info = EventInfo("mozi", url, name.strip(), parsed_start_datetime, address)
            movies.append(info)

        else:
            # TODO: Error handling
            ()

    return movies
