"""
Houses all functions to which web requests are dispatched. i.e. web handlers
"""


async def healthcheck() -> dict[str, str]:
    return {"status": "healthy"}


async def say_hello(name: str) -> dict[str, str]:
    return {"message": f"Hello {name}"}
