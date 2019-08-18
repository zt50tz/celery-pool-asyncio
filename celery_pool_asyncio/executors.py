import sys
import asyncio
from threading import Thread
from celery.concurrency import base
from .tracer import build_async_tracer
from billiard.einfo import ExceptionInfo
from celery.app import trace
from kombu.serialization import loads as loads_message


async def task_coro(
    coro_function,
    uuid,
    coro_args,
    coro_kwargs,
    request,
    accept_callback=None,
    callback=None,  # on_success
    timeout_callback=None,
    error_callback=None,
    soft_timeout=None,
    timeout=None,
    **options,
):
    app = coro_function.app

    accept_callback and accept_callback(
        base.os.getpid(),
        base.monotonic(),
    )

    try:
        coro_function.__trace__ = build_async_tracer(
            coro_function.name,
            coro_function,
            eager=True,
            propagate=app.conf.task_eager_propagates,
            app=app,
        )

        trace_ok_coro = coro_function.__trace__(
            uuid,
            coro_args,
            coro_kwargs,
            request,
        )

        try:
            retval = await asyncio.wait_for(trace_ok_coro, timeout)
        except asyncio.TimeoutError:
            timeout_callback and timeout_callback(soft_timeout, timeout)
            raise

        callback and callback((0, retval, base.monotonic()))

    except Exception as e:
        type_, _, tb = sys.exc_info()
        reason = e
        EI = ExceptionInfo((type_, reason, tb))
        error_callback and error_callback(
            EI,
            base.monotonic(),
        )


class TaskPool(base.BasePool):
    signal_safe = False
    is_green = False
    task_join_will_block = False

    def on_start(self):
        self._pool = asyncio.get_event_loop()
        self.loop_runner = Thread(target=self._pool.run_forever)
        self.loop_runner.daemon = True
        self.loop_runner.start()

    def on_stop(self):
        """Gracefully stop the pool."""
        self._pool.stop()
        yield from self._pool.shutdown_asyncgens()
        self._pool.close()

    def on_terminate(self):
        """Force terminate the pool."""
        self._pool.stop()
        self._pool.close()

    def restart(self):
        self.on_stop()
        self.on_start()

    def on_apply(
        self,
        target,
        args,
        kwargs=None,
        **options,
    ):
        task, uuid, request, body, content_type, content_encoding = args

        _, accept, hostname = trace._localized

        task_args, task_kwargs, task_embed = loads_message(
            body, content_type, content_encoding, accept=accept,
        )

        request.update({
            'args': args,
            'kwargs': kwargs,
            'hostname': hostname,
            'is_eager': False,
        }, **task_embed or {})

        target_task = self.app.tasks[task]

        coro = task_coro(
            target_task,
            uuid,
            task_args,
            task_kwargs,
            request,
            **options,
        )

        asyncio.run_coroutine_threadsafe(
            coro,
            self._pool,
        )
