Celery Pool AsyncIO
===============

![python](https://img.shields.io/pypi/pyversions/celery-pool-asyncio.svg)
![version](https://img.shields.io/pypi/v/celery-pool-asyncio.svg)
![downloads](https://img.shields.io/pypi/dm/celery-pool-asyncio.svg)
![format](https://img.shields.io/pypi/format/celery-pool-asyncio.svg)


![Logo](https://repository-images.githubusercontent.com/198568368/35298e00-c1e8-11e9-8bcf-76c57ee28db8)

* Free software: Apache Software License 2.0

Features
--------


```
import asyncio
from celery import Celery

# celery_pool_asyncio importing is optional
# It imports when you run worker or beat if you define pool or scheduler
# but it does not imports when you open REPL or when you run web application.
# If you want to apply monkey patches anyway to make identical environment
# when you use REPL or run web application app it's good idea to import
# celery_pool_asyncio module
import celery_pool_asyncio  # noqa
# Sometimes noqa does not disable linter (Spyder IDE)
celery_pool_asyncio.__package__


app = Celery()


@app.task(
    bind=True,
    soft_time_limit=42,  # raises celery.exceptions.SoftTimeLimitExceeded inside the coroutine
    time_limit=300,  # breaks coroutine execution
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

There are many monkey patches should be applied to make application working, and
some of them should be applied as early as possible. You are able to switch off
any of them by setting environment variable `CPA_MONKEY_DENY`. Remember you
should have a great reason to do it.

Except critical for work features it allows:
```
# await data sending to broker
async_result = await my_simple_task.delay()

# await wainting for AsyncResult
result = await async_result.get()
```

You can manually disable any of them by enumerating it comma separated:
```
$ env CPA_MONKEY_DENY=CELERY.SEND_TASK,ALL_BACKENDS celery worker -A hello_async_celery.app -P celery_pool_asyncio:TaskPool
```

Disabling is available for:
- `SIGNAL.SEND`
- `CELERY.SEND_TASK`
- `WORKCONTROLLER.USE_EVENTLOOP`
- `WORKER.CPU_COUNT`
- `BASERESULTCONSUMER.WAIT_FOR_PENDING`
- `BASERESULTCONSUMER.DRAIN_EVENTS_UNTIL`
- `ASYNCBACKENDMIXIN.WAIT_FOR_PENDING`
- `ALL_BACKENDS`
- `BEAT.SERVICE.START`
- `BEAT.SERVICE.STOP`
- `BUILD_TRACER`
- `KOMBU.UTILS.COMPAT`
- `RPC.RESULTCONSUMER.DRAIN_EVENTS`
- `AMQPBACKEND.DRAIN_EVENTS`
- `AMQPBACKEND.GET_MANY`
- `AMQP_BACKEND`
- `RPC_BACKEND`


[Scheduling](https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#starting-the-scheduler)
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
That's why it's good idea to run scheduler in separated process.


[Celery Signals](https://docs.celeryproject.org/en/stable/userguide/signals.html)
--------
```
from celery.signals import worker_init, worker_shutting_down


@worker_init.connect
async def do_startup_async(sender, **kwargs):
    # Coroutine functions are available after pool initialized
    await MyClass.init_async()


@worker_init.connect
def do_startup(sender, **kwargs):
    # regular functions are available too
    pass


@worker_shutting_down.connect
async def do_shutdown(sender=None, **kwargs):
    await MyClass.shutdown()
```

More examples
--------
There is an example project uses [celery-pool-asyncio](https://github.com/kai3341/celery-decorator-taskcls-example).
