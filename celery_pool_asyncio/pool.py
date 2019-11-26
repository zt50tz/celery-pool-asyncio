import asyncio
from threading import Thread


loop = None
loop_runner = None


def setup():
    global loop
    global loop_runner
    
    if loop is not None:
        return

    loop = asyncio.get_event_loop()
    loop_runner = Thread(target=loop.run_forever)
    loop_runner.daemon = True
    loop_runner.start()


def run_initialized(coro):
    return asyncio.run_coroutine_threadsafe(
        coro,
        loop,
    )


def run_uninitialized(coro):
    global run
    setup()
    run = run_initialized
    return run_initialized(coro)


run = run_uninitialized

