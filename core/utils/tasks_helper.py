def check_task_failed(task, raise_exception=False,
                      delete_instances_on_fail=[]):
    result = task.get(propagate=False)
    failed = task.failed()
    if failed:
        for instance in delete_instances_on_fail:
            instance.delete()
        if raise_exception:
            raise result
    return failed
