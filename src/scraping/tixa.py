from __future__ import annotations

import json
from datetime import datetime
from typing import List

import parsel
import requests

from src.db import EventInfo


def __get_tixa_concerts(url: str) -> List[EventInfo]:
    html_data = requests.get(url).text

    selector = parsel.Selector(text=html_data)

    json_data = [
        json.loads(json_data)
        for json_data in selector.xpath(
            ".//script[@type='application/ld+json']/text()"
        ).getall()
    ]
    concert_data = [
        concert
        for entry in json_data
        if entry["@id"] == "locationEvents"
        for concert in entry["itemListElement"]
    ]

    concerts = []
    for concert in concert_data:
        url = concert["item"]["url"]
        start_datetime = concert["item"]["startDate"]
        address = concert["item"]["location"]["name"]
        name = concert["item"]["name"]

        if (
            url is not None
            and start_datetime is not None
            and address is not None
            and name is not None
        ):
            parsed_start_datetime = datetime.strptime(
                start_datetime,
                "%Y-%m-%dT%H:%M:%S%z",
            )
            info = EventInfo("koncert", url, name, parsed_start_datetime, address)
            concerts.append(info)

        else:
            # TODO: Error handling
            ()

    return concerts


def get_budapest_park_concerts() -> List[EventInfo]:
    return __get_tixa_concerts("https://tixa.hu/budapest_park")


def get_durer_kert_concerts() -> List[EventInfo]:
    return __get_tixa_concerts("https://tixa.hu/durerkert")


def get_turbina_concerts() -> List[EventInfo]:
    return __get_tixa_concerts("https://tixa.hu/turbina-kulturalis-kozpont")
