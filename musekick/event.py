from abc import ABC
from typing import Optional
from dataclasses import dataclass
import datetime as dt

from .base import SongkickObject
from .artist import Artist
from .venue import Venue


@dataclass
class EventDetails:
    artists: list[Artist]
    venue: Venue
    dates: tuple[dt.date, dt.date]
    additional: dict[str, str]


class Event(SongkickObject[EventDetails], ABC):
    pass


class Concert(Event):
    def __init__(
        self,
        concert_id: str,
        name: Optional[str],
        details: Optional[EventDetails] = None,
    ):
        self.id = concert_id
        super().__init__(name, details)

    def url(self):
        return f"https://www.songkick.com/concerts/{self.id}"

    async def _get_details(self) -> EventDetails:
        root = await self._selector()

        date_str = root.css("div.date-and-name").css("p::text").get()
        dates = parse_dates(date_str)

        artists = []
        for li in root.css("div.expanded-lineup-details").css("li"):
            artist_ln = li.css("div.main-details").css("a")
            aid = artist_ln.attrib["href"].split("/")[-1]
            name = artist_ln.css("::text").get()
            artists.append(Artist(aid, name))

        venue_ln = root.css("div.location").css("span.name").css("a")[0]
        v_id = venue_ln.attrib["href"].split("/")[-1]
        v_name = venue_ln.css("::text").get()
        # todo: venue address

        # todo: additional details

        return EventDetails(
            artists, Venue(v_id, None, None, name=v_name), dates, dict()
        )


@dataclass
class FestivalSeriesDetails:
    name: str


class FestivalSeries(SongkickObject[FestivalSeriesDetails]):
    def __init__(
        self,
        series_id: str,
        name: Optional[str],
        details: Optional[FestivalSeriesDetails] = None,
    ) -> None:
        self.id = series_id
        super().__init__(name, details)

    def url(self):
        return f"https://www.songkick.com/festivals/{self.series_id}"

    async def _get_details(self) -> FestivalSeriesDetails:
        root = await self._selector()
        name = root.css("div.primary-container").css("h1::text").get()
        return FestivalSeriesDetails(name)


def parse_date(s: str):
    return dt.datetime.strptime(s.strip(), "%A %d %B %Y").date()


# U+2013, not a hyphen
SPLITTER = "–"


def parse_dates(s: str) -> tuple[dt.date, dt.date]:
    tup = tuple(parse_date(d) for d in s.split(SPLITTER))
    if len(tup) == 1:
        tup *= 2
    return tup


class Festival(Event):
    def __init__(
        self,
        festival_id: str,
        series: FestivalSeries,
        name: Optional[str],
        details: Optional[EventDetails] = None,
    ) -> None:
        self.id = festival_id
        self.series = series
        super().__init__(name, details)

    def url(self):
        return f"https://www.songkick.com/festivals/{self.series.id}/id/{self.id}"

    async def _get_details(self) -> EventDetails:
        root = await self._selector()

        date_str = root.css("div.date-and-name").css("p::text").get()
        dates = parse_dates(date_str)

        artists = []
        for li in root.css("#lineup").css("li").css("a"):
            name = li.css("::text").get()
            aid = li.attrib["href"].split("/")[-1]
            artists.append(Artist(aid, name))

        venue_ln = root.css("div.venue-info-details").css("a.url")[0]
        v_id = venue_ln.attrib["href"].split("/")[-1]
        v_name = venue_ln.css("::text").get()
        # todo: address lines, contact
        venue = Venue(v_id, None, None, v_name)

        # todo: additional details

        return EventDetails(artists, venue, dates, dict())
