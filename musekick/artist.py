from dataclasses import dataclass
from typing import Optional

from .base import SongkickObject


@dataclass
class ArtistDetails:
    name: str


class Artist(SongkickObject[ArtistDetails]):
    def __init__(
        self,
        artist_id: str,
        name: Optional[str] = None,
        details: Optional[ArtistDetails] = None,
    ) -> None:
        self.id = artist_id
        if details is None and name is not None:
            details = ArtistDetails(name)

        super().__init__(name, details)

    def url(self):
        return f"https://www.songkick.com/artists/{self.id}"

    async def _get_details(self) -> ArtistDetails:
        page = await self._selector()
        name = page.css("div.artist-overview").css("h1.h0::text").get()
        return ArtistDetails(name)
