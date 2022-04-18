# coding: utf8

import asyncio
import os
from random import randint

from update_state_app import celery, simple_task, celery_states

NUM_CELERY_TASKS = 10


async def run_simple():
    tasks = []
    for _ in range(NUM_CELERY_TASKS):
        times = randint(3, 6)
        tasks.append({
            'times': times,
            'state': None,
            'current': 0,
            'uuid': str(await simple_task.delay(times)),
            'completed': False
        })
    while True:
        await asyncio.sleep(0.1)
        all_done = True
        os.system('clear')
        for task in tasks:
            result = celery.AsyncResult(task['uuid'])
            task['state'] = result.state
            if result.state == celery_states.FAILURE:
                pass
            else:
                if isinstance(result.info, dict):
                    task['current'] = result.info['time']
                if task['current'] >= task['times'] or result.state == celery_states.SUCCESS:
                    task['completed'] = True
                else:
                    all_done = False
            label = [task['uuid'], task['state'], str(task['times']), str(task['current'])]
            print(' - '.join(label))
        if all_done:
            break
    print('Completed')

if __name__ == "__main__":
    asyncio.run(run_simple())
