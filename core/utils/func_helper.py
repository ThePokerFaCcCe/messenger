from typing import Callable


def delete_instance_on_error(func: Callable, instance,
                             *func_args, **func_kwargs):
    try:
        func(*func_args, **func_kwargs)
    except Exception as e:
        instance.delete()
        raise e
