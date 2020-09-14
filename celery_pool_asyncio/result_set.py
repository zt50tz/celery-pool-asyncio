async def join(self, timeout=None, propagate=True, interval=0.5,
         callback=None, no_ack=True, on_message=None,
         disable_sync_subtasks=True, on_interval=None):
    """Gather the results of all tasks as a list in order.

    Note:
        This can be an expensive operation for result store
        backends that must resort to polling (e.g., database).

        You should consider using :meth:`join_native` if your backend
        supports it.

    Warning:
        Waiting for tasks within a task may lead to deadlocks.
        Please see :ref:`task-synchronous-subtasks`.

    Arguments:
        timeout (float): The number of seconds to wait for results
            before the operation times out.
        propagate (bool): If any of the tasks raises an exception,
            the exception will be re-raised when this flag is set.
        interval (float): Time to wait (in seconds) before retrying to
            retrieve a result from the set.  Note that this does not have
            any effect when using the amqp result store backend,
            as it does not use polling.
        callback (Callable): Optional callback to be called for every
            result received.  Must have signature ``(task_id, value)``
            No results will be returned by this function if a callback
            is specified.  The order of results is also arbitrary when a
            callback is used.  To get access to the result object for
            a particular id you'll have to generate an index first:
            ``index = {r.id: r for r in gres.results.values()}``
            Or you can create new result objects on the fly:
            ``result = app.AsyncResult(task_id)`` (both will
            take advantage of the backend cache anyway).
        no_ack (bool): Automatic message acknowledgment (Note that if this
            is set to :const:`False` then the messages
            *will not be acknowledged*).
        disable_sync_subtasks (bool): Disable tasks to wait for sub tasks
            this is the default configuration. CAUTION do not enable this
            unless you must.

    Raises:
        celery.exceptions.TimeoutError: if ``timeout`` isn't
            :const:`None` and the operation takes longer than ``timeout``
            seconds.
    """
    if disable_sync_subtasks:
        assert_will_not_block()
    time_start = monotonic()
    remaining = None

    if on_message is not None:
        raise ImproperlyConfigured(
            'Backend does not support on_message callback')

    results = []
    for result in self.results:
        remaining = None
        if timeout:
            remaining = timeout - (monotonic() - time_start)
            if remaining <= 0.0:
                raise TimeoutError('join operation timed out')
        value = await result.get(
            timeout=remaining, propagate=propagate,
            interval=interval, no_ack=no_ack, on_interval=on_interval,
            disable_sync_subtasks=disable_sync_subtasks,
        )
        if callback:
            callback(result.id, value)
        else:
            results.append(value)
    return results


async def join_native(self, timeout=None, propagate=True,
                interval=0.5, callback=None, no_ack=True,
                on_message=None, on_interval=None,
                disable_sync_subtasks=True):
    """Backend optimized version of :meth:`join`.

    .. versionadded:: 2.2

    Note that this does not support collecting the results
    for different task types using different backends.

    This is currently only supported by the amqp, Redis and cache
    result backends.
    """
    if disable_sync_subtasks:
        assert_will_not_block()
    order_index = None if callback else {
        result.id: i for i, result in enumerate(self.results)
    }
    acc = None if callback else [None for _ in range(len(self))]
    for task_id, meta in self.iter_native(timeout, interval, no_ack,
                                          on_message, on_interval):
        if isinstance(meta, list):
            value = []
            for children_result in meta:
                res = await children_result.get()
                value.append(res)
        else:
            value = meta['result']
            if propagate and meta['status'] in states.PROPAGATE_STATES:
                raise value
        if callback:
            callback(task_id, value)
        else:
            acc[order_index[task_id]] = value
    return acc
