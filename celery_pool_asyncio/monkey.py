from .monkey_utils import to_async

from . import backends
from . import worker
from . import asynchronous as local_asynchronous


def patch_send_task(as_task=True):
    """Celery task sending can be optionally awaited"""
    from celery.app import Celery
    Celery.send_task = to_async(Celery.send_task, as_task)


def patch(as_task=True):
    """Apply all patches"""
    patch_send_task(as_task)
    worker.patch_worker()
    local_asynchronous.patch_result()
    backends.patch_backends()
