from celery.app import task
from asgiref import sync


def patch():
    apply_async = task.Task.apply_async
    apply_async = sync.sync_to_async(apply_async)
    task.Task.apply_async = apply_async
