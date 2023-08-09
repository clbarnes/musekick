from typing import Optional
from dataclasses import dataclass
from musekick.base import SongkickObject
from musekick.event import Event, Concert, Festival, FestivalSeries


@dataclass
class UserDetails:
    upcoming: list[Event]


class User(SongkickObject[UserDetails]):
    def url(self):
        return f"https://www.songkick.com/users/{self.name}/calendar"

    async def _get_details(self) -> UserDetails:
        root = await self._selector()
        events: list[Event] = []
        for li in root.css("#event-listings").css("ul").css("li"):
            if "with-date" in li.attrib.get("class", ""):
                continue
            a = li.css("p.artists.summary").css("a")
            name = a.css("strong::text").get()
            parts = a.attrib["href"].split("/")
            if parts[-2] == "concerts":
                events.append(Concert(parts[-1], name))
            else:
                events.append(
                    Festival(parts[-1], FestivalSeries(parts[-3], None), name)
                )
        return UserDetails(events)
