from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar
import logging

from parsel import Selector

from .client import global_client

logger = logging.getLogger(__name__)

D = TypeVar("D")


class SongkickObject(ABC, Generic[D]):
    def __init__(self, name: Optional[str], details: Optional[D] = None) -> None:
        self._name = name
        self._details = details

    @abstractmethod
    def url(self) -> str:
        pass

    async def _selector(self) -> Selector:
        client = global_client()
        page = await client.get(self.url())
        page.raise_for_status()
        return Selector(page.text)

    @abstractmethod
    async def _get_details(self) -> D:
        pass

    async def details(self) -> D:
        if self._details is None:
            self._details = await self._get_details()
        return self._details

    @property
    def name(self) -> Optional[str]:
        if self._name is None:
            if self.details is None:
                return None
            else:
                return getattr(self.details, "name", None)
        return self._name
