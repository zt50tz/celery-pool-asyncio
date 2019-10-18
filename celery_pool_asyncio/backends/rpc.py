import asyncio


async def drain_events(self, timeout=None):
    if self._connection:
        coro = self._connection.drain_events(timeout=timeout)
        if coro:
            yield await coro
    elif timeout:
        await asyncio.sleep(timeout)


def patch_backend():
    from celery.backends import rpc
    ResultConsumer = rpc.ResultConsumer
    ResultConsumer._original_drain_events = ResultConsumer.drain_events
    ResultConsumer.drain_events = drain_events
