def check_task_failed(task, raise_exception=False,
                      delete_instances_on_fail=[]):
    failed = task.failed()
    if failed:
        for instance in delete_instances_on_fail:
            instance.delete()
        if raise_exception:
            raise task
    return failed
