from __future__ import annotations
from functools import wraps
from typing import Optional, Union
from httpx import AsyncClient
import asyncio
import logging
import datetime as dt

logger = logging.getLogger(__name__)

_client: Optional[RateLimitedClient] = None

INTERVAL = 1
BASE_URL = "https://www.songkick.com"

EDGE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67"

_background_tasks = set()


class RateLimitedClient(AsyncClient):
    """httpx.AsyncClient with a rate limit."""

    def __init__(self, interval: Union[dt.timedelta, float], count=1, **kwargs):
        """
        Parameters
        ----------
        interval : Union[dt.timedelta, float]
            Length of interval.
            If a float is given, seconds are assumed.
        numerator : int, optional
            Number of requests which can be sent in any given interval (default 1).
        """
        if isinstance(interval, dt.timedelta):
            interval = interval.total_seconds()

        self.interval = interval
        self.semaphore = asyncio.Semaphore(count)
        super().__init__(**kwargs)

    def _schedule_semaphore_release(self):
        wait = asyncio.create_task(asyncio.sleep(self.interval))
        _background_tasks.add(wait)

        def wait_cb(task):
            self.semaphore.release()
            _background_tasks.discard(task)

        wait.add_done_callback(wait_cb)

    @wraps(AsyncClient.send)
    async def send(self, *args, **kwargs):
        await self.semaphore.acquire()
        send = asyncio.create_task(super().send(*args, **kwargs))
        self._schedule_semaphore_release()
        return await send


def make_client() -> RateLimitedClient:
    return RateLimitedClient(
        INTERVAL,
        10,
        base_url=BASE_URL,
        timeout=30,
        headers={"user-agent": EDGE_USER_AGENT},
    )


def global_client(client: Optional[RateLimitedClient] = None) -> RateLimitedClient:
    global _client
    if client is not None:
        _client = client

    if _client is None or _client.is_closed:
        _client = make_client()

    return _client


def get_client() -> RateLimitedClient:
    if _client is None:
        raise ValueError("No global client; use `async with global_client()`: block")
    if _client.is_closed:
        raise ValueError(
            "Global client is closed; use `async with global_client()` block"
        )
    return _client
