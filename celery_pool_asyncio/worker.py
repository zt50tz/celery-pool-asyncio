def should_use_eventloop(self):
    return True


def patch_worker():
    from celery.worker import worker
    WorkController = worker.WorkController
    WorkController.should_use_eventloop = should_use_eventloop
