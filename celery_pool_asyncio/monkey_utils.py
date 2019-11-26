import asyncio
from asgiref import sync

from . import pool


def gentask(corofunc):
    def wrapper(*args, **kwargs):
        coro = corofunc(*args, **kwargs)
        return asyncio.create_task(coro)
    return wrapper


def to_async(callback, as_task=False):
    corofunc = sync.sync_to_async(callback)

    if as_task and pool.loop:
        print(callback)
        corofunc = gentask(corofunc)

    return corofunc
