# coding: utf8

import asyncio

# Importing Celery
from celery import Celery
from celery import states as celery_states

# Importing Async
import celery_pool_asyncio
celery_pool_asyncio.__package__


# Configure
celery = Celery(__name__)
celery.conf.broker_url = 'redis://localhost:6379/10'
celery.conf.result_backend = 'redis://localhost:6379/10'


# Override task class
class ContextTask(celery.Task):
    async def __call__(self, *args, **kwargs):
        # Updating state, so flower can show that it was started
        self.update_state(task_id=kwargs['celery_task_uuid'], state=celery_states.STARTED)
        return await self.run(*args, **kwargs)


celery.Task = ContextTask


# Define simple task
@celery.task(bind=True)
async def simple_task(task, times, **kwargs):
    time = 0
    while time < times:
        await asyncio.sleep(1)
        time += 1
        task.update_state(task_id=kwargs['celery_task_uuid'], state='INPROGRESS', meta={'time': time})
        print(f'{kwargs["celery_task_uuid"]} [{times} / {time}]')
    return {'time': time}
