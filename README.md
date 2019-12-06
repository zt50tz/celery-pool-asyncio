Celery Pool AsyncIO
===============

![Logo](https://repository-images.githubusercontent.com/198568368/35298e00-c1e8-11e9-8bcf-76c57ee28db8)

* Free software: Apache Software License 2.0

Features
--------


```
import asyncio
from celery import Celery
from celery_pool_asyncio import monkey as cpa_monkey

# Apply monkey patches before creating celery app
cpa_monkey.patch()

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

Monkey patching: wtf and why
--------

There are many monkey patches applies automatically, but some of them are
optional or may change application behavior. It's ok in general, but exceptions
are possible. That's why it's good idea to apply it manually.

Allows:
```
async_result = await my_simple_task.delay()
result = await async_result.get()
```

Manual targets:
- `celery.app.Celery.send_task`
- `celery.worker.worker.WorkController.should_use_eventloop`
- `celery.backends.asynchronous.BaseResultConsumer._wait_for_pending`
- `celery.backends.asynchronous.BaseResultConsumer.drain_events_until`
- `celery.backends.asynchronous.AsyncBackendMixin.wait_for_pending`
- `celery.backends.amqp.AMQPBackend.drain_events`
- `celery.backends.amqp.AMQPBackend.get_many`
- `celery.backends.rpc.ResultConsumer.drain_events`

Scheduling
--------

Default scheduler doesn't work. `PersistentScheduler` is subclass of default
celery scheduler.

Running celery with scheduler:
```
$ celery worker -A hello_async_celery.app -P celery_pool_asyncio:TaskPool --scheduler celery_pool_asyncio:PersistentScheduler
$ celery beat -A hello_async_celery.app --scheduler celery_pool_asyncio:PersistentScheduler
```

Embeding also supported:
```
$ celery worker -A hello_async_celery.app -P celery_pool_asyncio:TaskPool --scheduler celery_pool_asyncio:PersistentScheduler -B
```

WARNING: embeded scheduler startup is not stable. It starts correctly in ~50%
of cases. It looks like race condition. But after correct startup it works well.

More examples
--------
There is an example project uses `celery-pool-asyncio`:
https://github.com/kai3341/celery-decorator-taskcls-example
