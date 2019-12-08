import os
from .monkey_utils import to_async

def init_deny_targets():
    """Read and parse environment variable"""
    deny_targets = os.getenv('CPA_MONKEY_DENY')

    if not deny_targets:
        return frozenset()

    deny_targets = deny_targets.split(',')
    return frozenset(deny_targets)


deny_targets = init_deny_targets()

# --- Apply all patches ---

from . import backends
from . import worker
from . import beat
from . import asynchronous
from . import tracer
from . import drainer


# --- celery.app.Celery
from celery.app import Celery

if 'CELERY.SEND_TASK' not in deny_targets:
    """Celery task sending can be awaited"""
    Celery.send_task = to_async(Celery.send_task, True)


# --- celery.worker.worker.WorkController
from celery.worker.worker import WorkController

if 'WORKCONTROLLER.USE_EVENTLOOP' not in deny_targets:
    WorkController.should_use_eventloop = worker.should_use_eventloop

# --- celery.backends.asynchronous.BaseResultConsumer
from celery.backends.asynchronous import BaseResultConsumer

if 'BASERESULTCONSUMER.WAIT_FOR_PENDING' not in deny_targets:
    BaseResultConsumer._wait_for_pending = asynchronous._wait_for_pending

if 'BASERESULTCONSUMER.DRAIN_EVENTS_UNTIL' not in deny_targets:
    BaseResultConsumer.drain_events_until = asynchronous.drain_events_until

# --- celery.backends.asynchronous.AsyncBackendMixin
from celery.backends.asynchronous import AsyncBackendMixin

if 'ASYNCBACKENDMIXIN.WAIT_FOR_PENDING' not in deny_targets:
    AsyncBackendMixin.wait_for_pending = asynchronous.wait_for_pending


if 'ALL_BACKENDS' not in deny_targets:
    """Celery AsyncResult.get() can be awaited"""
    backends.patch_backends()


# --- celery.beat.Service
Service = beat.beat.Service

if 'BEAT.SERVICE.START' not in deny_targets:
    Service.start = beat.Service__start
    Service.async_start = beat.Service__async_start
    Service.async_run = beat.Service__async_run

if 'BEAT.SERVICE.STOP' not in deny_targets:
    Service.stop = beat.Service__stop


# --- celery.app.trace.build_tracer
if 'BUILD_TRACER' not in deny_targets:
    tracer.trace.build_tracer = tracer.build_async_tracer

# --- kombu.utils.compat
from kombu.utils import compat

if 'KOMBU.UTILS.COMPAT' not in deny_targets:
    compat._detect_environment = drainer._detect_environment
