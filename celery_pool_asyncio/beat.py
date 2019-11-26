import asyncio

from . import pool


async def apply_async(self, entry, producer=None, advance=True, **kwargs):
    # Update time-stamps and run counts before we actually execute,
    # so we have that done if an exception is raised (doesn't schedule
    # forever.)
    entry = self.reserve(entry) if advance else entry
    task = self.app.tasks.get(entry.task)

    try:
        if task:
            return await task.apply_async(entry.args, entry.kwargs,
                                    producer=producer,
                                    **entry.options)
        else:
            return await self.send_task(entry.task, entry.args, entry.kwargs,
                                  producer=producer,
                                  **entry.options)
    except Exception as exc:  # pylint: disable=broad-except
        reraise(SchedulingError, SchedulingError(
            "Couldn't apply scheduled task {0.name}: {exc}".format(
                entry, exc=exc)), sys.exc_info()[2])
    finally:
        self._tasks_since_sync += 1
        if self.should_sync():
            self._do_sync()


def apply_entry(self, entry, producer=None):
    info('Scheduler: Sending due task %s (%s)', entry.name, entry.task)
    try:
         coro = self.apply_async(entry, producer=producer, advance=False)
         result = pool.run(coro)
    except Exception as exc:  # pylint: disable=broad-except
        error('Message Error: %s\n%s',
              exc, traceback.format_stack(), exc_info=True)
    else:
        debug('%s sent. id->%s', entry.task, result.id)


def patch_beat():
    print('patch_beat')
    from celery import beat
    ScheduleEntry = beat.ScheduleEntry
    ScheduleEntry.apply_async = apply_async
    ScheduleEntry.apply_entry = apply_entry

