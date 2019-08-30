import asyncio
from celery.app import Celery
from asgiref import sync


def gentask(corofunc):
    def wrapper(*args, **kwargs):
        coro = corofunc(*args, **kwargs)
        return asyncio.create_task(coro)
    return wrapper
        

def patch(as_task=False):
    send_task = Celery.send_task
    send_task = sync.sync_to_async(send_task)

    if as_task:
        send_task = gentask(send_task)

    Celery.send_task = send_task
