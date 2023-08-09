from dataclasses import dataclass
from typing import Optional

from .base import SongkickObject


@dataclass
class VenueDetails:
    name: str
    address_lines: list[str]
    contact: str


class Venue(SongkickObject[VenueDetails]):
    def __init__(
        self,
        venue_id: str,
        address_lines: Optional[list[str]],
        contact: Optional[str],
        name: Optional[str],
        details: Optional[VenueDetails] = None,
    ) -> None:
        self.id = venue_id
        self._address_lines = address_lines
        self._contact = contact
        super().__init__(name, details)

    @property
    def address_lines(self) -> Optional[list[str]]:
        if self._address_lines is None:
            if self.details is None:
                return None
            else:
                return getattr(self.details, "address_lines", None)
        return self._address_lines

    @property
    def contact(self) -> Optional[str]:
        if self._contact is None:
            if self.details is None:
                return None
            else:
                return getattr(self.details, "contact", None)
        return self._contact

    def url(self):
        return f"https://www.songkick.com/venues/{self.id}"

    async def _get_details(self) -> VenueDetails:
        root = await self._selector()
        brief = root.css("div.component.brief.location.vcard")
        name = brief.css("h1.h0::text").get().strip().rstrip("-").strip()
        details = brief.css("p.venue-hcard")
        spans = details.xpath("span")
        addr = [s.css("::text").get() for s in spans[0].xpath("span")]
        contact = spans[1].css("::text").get()
        return VenueDetails(name, addr, contact)
