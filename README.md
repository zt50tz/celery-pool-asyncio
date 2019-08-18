Celery Pool AsyncIO
===============

![Logo](https://repository-images.githubusercontent.com/198568368/35298e00-c1e8-11e9-8bcf-76c57ee28db8)

* Free software: Apache Software License 2.0

Features
--------


```
import asyncio
from celery import Celery

app = Celery()


@app.task(
    bind=True,
    soft_time_limit=None,  # temporary unimplemented. You can help me
    time_limit=300,  # raises futures.TimeoutError on timeout
)
async def my_task(self, *args, **kwargs):
    await asyncio.sleep(5)


@app.task
async def my_simple_task(*args, **kwargs):
    await asyncio.sleep(5)
```

Then run celery:

```
$ celery worker -A hello_async_celery.app -P celery_pool_asyncio:TaskPool
```

