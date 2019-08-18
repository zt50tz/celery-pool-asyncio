#!/usr/bin/env python

import pathlib
import asyncio
import time
from pprint import pformat
#from concurrent.futures import TimeoutError

import pytest
from kombu import Queue


from celery_pool_asyncio import TaskPool

root = pathlib.Path()
brocker = root / 'brocker'
brocker.mkdir(exist_ok=True)

dir_messages = brocker / 'messages'
dir_messages.mkdir(exist_ok=True)

dir_out = brocker / 'out'
dir_out.mkdir(exist_ok=True)

dir_processed = brocker / 'processed'
dir_processed.mkdir(exist_ok=True)

async def tack_function(input_data):
    await asyncio.sleep(1)
    return input_data.upper()


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'filesystem:// %s' % dir_messages,
        'broker_transport_options': {
            'data_folder_in': '%s' % dir_out,
            'data_folder_out': '%s' % dir_out,
            'data_folder_processed': '%s' % dir_processed,
        },
        'result_persistent': True,
    }


@pytest.fixture(scope='session')
def celery_includes():
    return [
        'tests.test_celery_pool_asyncio',
    ]


@pytest.fixture(scope='session')
def celery_worker_pool():
    return 'celery_pool_asyncio:TaskPool'


def test_create_task(celery_app, celery_worker):
    @celery_app.task
    async def tack_function(input_data):
        await asyncio.sleep(1)
        print('tack_function', input_data)
        return input_data.upper()

    task = tack_function.delay('hello, world!')
    print('task', task)
    result = task.get(timeout=10)
    print('result', result)

