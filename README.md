# musekick

Unofficial songkick client for information not requiring login.

## Example usage

```python
import asyncio as aio
from musekick.calendar import User
from musekick.client import global_client

USERNAME = "someusername"

async def amain():
    """Print all artists in user's "upcoming" calendar.

    Order is arbitrary.
    """
    user = User(USERNAME)
    async with global_client():
        udets = await user.details()

        for edets in aio.as_completed([e.details() for e in udets.upcoming]):
            for a in (await edets).artists:
                print(a.name)


if __name__ == "__main__":
    aio.run(amain())
```
