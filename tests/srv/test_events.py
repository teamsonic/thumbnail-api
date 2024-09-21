import pytest

from app.srv import app
from app.srv.events import lifespan


@pytest.mark.asyncio
async def test_events() -> None:
    """Very superficial test.

    Run the lifespan event and make sure no unexpected exceptions are raised.
    """
    async with lifespan(app) as l:
        pass
