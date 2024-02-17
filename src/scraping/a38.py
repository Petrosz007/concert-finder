from __future__ import annotations

from datetime import datetime
from typing import List

import parsel
import requests

from ..db import EventInfo


def get_a38_concerts() -> List[EventInfo]:
    html_data = requests.get("https://www.a38.hu/hu/programok").text

    selector = parsel.Selector(text=html_data)

    concerts = []
    for event in selector.css("ul#eventList>li"):
        url = event.xpath(".//meta[@itemprop='url']/@content").get()
        start_datetime = event.xpath(".//meta[@itemprop='startDate']/@content").get()
        address = event.xpath(".//link[@itemprop='address']/@content").get()
        name = event.xpath(".//h2[@itemprop='name']/div/text()").get()

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
            info = EventInfo(
                "koncert", url, name.strip(), parsed_start_datetime, address
            )
            concerts.append(info)

        else:
            # TODO: Error handling
            ()

    return concerts
