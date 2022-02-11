
def count_members(instance, field='members') -> int:
    count = getattr(instance, f'{field}_count', None)
    if count is None:
        count = getattr(instance, field).count()
    return count
