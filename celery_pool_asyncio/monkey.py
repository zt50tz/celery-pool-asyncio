import asyncio
from asgiref import sync


def _gentask(corofunc):
    def wrapper(*args, **kwargs):
        coro = corofunc(*args, **kwargs)
        return asyncio.create_task(coro)
    return wrapper


def _to_async(callback, as_task=True):
    corofunc = sync.sync_to_async(callback)

    if as_task:
        corofunc = _gentask(corofunc)

    return corofunc


def patch_send_task(as_task=True):
    """Celery task sending can be optionally awaited"""
    from celery.app import Celery
    Celery.send_task = _to_async(Celery.send_task, as_task)


def patch_result_get():
    """AsyncResult.get must be future, not task"""
    from celery.result import AsyncResult
    AsyncResult.get = _to_async(AsyncResult.get)


def patch(as_task=True):
    """Apply all patches"""
    patch_send_task(as_task)
    patch_result_get()
