from functools import lru_cache

from celery import beat
from redbeat import RedBeatScheduler
from redbeat.schedulers import get_redis, logger

from .scheduler import AsyncSchedulerMixin
from .monkey_utils import to_async


@lru_cache(max_size=3)
def pexpire_patched(app):
    redis = get_redis(app)
    pexpire = redis.pexpire
    return to_async(pexpire)


class RedBeatAsyncScheduler(AsyncSchedulerMixin, RedBeatScheduler):
    async def maybe_due(self, entry, **kwargs):
        is_due, next_time_to_run = entry.is_due()

        if is_due:
            logger.info(
                'Scheduler: Sending due task %s (%s)',
                entry.name,
                entry.task,
            )
            try:
                result = await self.apply_async(entry, **kwargs)
            except Exception as exc:
                logger.exception('Message Error: %s', exc)
            else:
                logger.debug('%s sent. id->%s', entry.task, result.id)
        return next_time_to_run

    async def tick(self, min=min, **kwargs):
        if self.lock:
            logger.debug('beat: Extending lock...')
            pexpire = pexpire_patched(self.app)
            await pexpire(self.lock_key, int(self.lock_timeout * 1000))

        remaining_times = []
        try:
            for entry in self.schedule.values():
                next_time_to_run = await self.maybe_due(
                    entry,
                    **self._maybe_due_kwargs,
                )
                if next_time_to_run:
                    remaining_times.append(next_time_to_run)
        except RuntimeError:
            logger.debug('beat: RuntimeError', exc_info=True)

        return min(remaining_times + [self.max_interval])
