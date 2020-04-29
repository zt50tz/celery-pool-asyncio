# Changelog

## [0.2.0]
- Allow to decorate corofunctions by `celery.signals`
- Implement pool capacity (`-c, --concurency`)

## [0.1.12]
- Finalize monkey patcher refactoring. Now you able to switch off applying of
any monkey patch. Remember with great power comes great responsibility
- Implement `soft_time_limit`
- Implement `revoke`
- Fix keywords

## [0.1.11]
- Total monkey patching refactor. Now it is enabled by default, but you can
manually disable some of features using environment variable `CPA_MONKEY_DENY`

## [0.1.10]
- Make Celery Beat working
    - Add async Celery Scheduler
    - More monkey patching
- Move loop and loop_runner to own module
    - Avoid creating multiple loops and loop_runners per application

## [0.1.9]
- Large rework of `await AsyncResult.get()`
    - Works much better than earlier, but it's crap still
    - Added outnumber of monkey-patches
- Fixed race condition on first microseconds of pool shutdown

## [0.1.8]
- Cleanup tracer, use celery.app.trace namespase where it possible

## [0.1.7]
- Refactor monkey, split it
- Move `patch_send_task` to own function
- Add `patch_result_get` to `await AsyncResult.get`

## [0.1.6]
- Avoid building trace twice
- Also this small performance optimization fixed `AsyncResult.get`

## [0.1.5]
- Fix graceful shutdown

## [0.1.4]
- Fix monkey: another function must be patched

## [0.1.3]
- Add changelog
- Append documentation

## [0.1.2]
- Add monkey patcher to make brocker IO operations nonblocking

## [0.1.1]
- Refactor code
- Fix found errors

## [0.1.0]
- Initial commit
