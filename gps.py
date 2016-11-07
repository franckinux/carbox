import asyncio
from concurrent.futures import CancelledError


async def poll():
    while True:
        # print("task2")
        try:
            await asyncio.sleep(1)
        except CancelledError:
            break
