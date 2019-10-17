from .monkey_utils import to_async


def patch_send_task(as_task=True):
    """Celery task sending can be optionally awaited"""
    from celery.app import Celery
    Celery.send_task = to_async(Celery.send_task, as_task)


def patch(as_task=True):
    """Apply all patches"""
    patch_send_task(as_task)
