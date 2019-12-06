import sys
import asyncio
from celery.concurrency import base
from billiard.einfo import ExceptionInfo
from celery.app import trace
from kombu.serialization import loads as loads_message

from . import pool
from . import tracer
from . import drainer


tracer.patch_trace()
drainer.setup_environment()


class TaskPool(base.BasePool):
    signal_safe = False
    is_green = False
    task_join_will_block = False

    def on_start(self):
        self.running_tasks = 0
        self.stopping = False

        coro = self.after_start()
        pool.run(coro)

    async def after_start(self):
        pass

    def on_stop(self):
        """Gracefully stop the pool."""
        self.stopping = True
        self.try_stop()
        pool.pool.join()

    def try_stop(self):
        """Shutdown should be happend after last task has been done"""
        if self.running_tasks == 0:
            coro = pool.pool and pool.pool.shutdown()
            coro and pool.run(coro)

    def on_terminate(self):
        """Force terminate the pool."""
        pool.loop.stop()
        yield from pool.loop.shutdown_asyncgens()
        pool.loop.close()
        pool.pool.stop()

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
        """Looks crazy"""
        (
            task,
            task_uuid,
            request,
            body,
            content_type,
            content_encoding,
        ) = args

        _, accept, hostname = trace._localized

        (
            task_args,
            task_kwargs,
            task_embed,
        ) = loads_message(
            body,
            content_type,
            content_encoding,
            accept=accept,
        )

        task_embed = task_embed or {}

        request.update({
            'args': args,
            'kwargs': kwargs,
            'hostname': hostname,
            'is_eager': False,
        }, **task_embed)

        target_task = self.app.tasks[task]

        coro = self.task_coro(
            target_task,
            task_uuid,
            task_args,
            task_kwargs,
            request,
            **options,
        )

        pool.run(coro)

    def __enter__(self):
        self.running_tasks += 1

    def __exit__(self, *args, **kwargs):
        self.running_tasks -= 1
        self.stopping and self.try_stop()

    async def task_coro(
        self,
        coro_function,
        task_uuid,
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
        if self.stopping:
            return

        with self:
            accept_callback and accept_callback(
                base.os.getpid(),
                base.monotonic(),
            )

            try:
                trace_ok_coro = coro_function.__trace__(
                    task_uuid,
                    coro_args,
                    coro_kwargs,
                    request,
                )

                try:
                    retval = await asyncio.wait_for(trace_ok_coro, timeout)
                    callback and callback((0, retval, base.monotonic()))
                except asyncio.TimeoutError:
                    timeout_callback and timeout_callback(
                        soft_timeout,
                        timeout,
                    )
                    raise

            except Exception as e:
                type_, _, tb = sys.exc_info()
                reason = e
                EI = ExceptionInfo((type_, reason, tb))
                error_callback and error_callback(
                    EI,
                    base.monotonic(),
                )
