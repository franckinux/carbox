import asyncio
import gbulb

from judebox import Judebox
from gps import poll


async def scheduler():
    judebox = Judebox()
    task1 = asyncio.ensure_future(judebox.judebox())
    task2 = asyncio.ensure_future(poll())
    await task1
    task2.cancel()
    await task2

gbulb.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(scheduler())
loop.close()
