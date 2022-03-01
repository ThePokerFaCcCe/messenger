def options(query_params: dict):
    '''
    options decorator that can be used for actions

    Parameters
    ----------
    :param `query_params`: A dict of params that should exist in query params. e.g:
    ```
    {
        "user_id":
        {
            # - REQUIRED:

            # Only one of either `type` or `regex` should set
            # if both set, AssertionError will be raised
            "type" : int,
            "regex":r'^(*)$', 

            # - OPTIONAL:

            "queryset" : User.objects.all(),
            "lookup" : "id", #lookup for filtering queryset. default is param key
        }
    }
    ```

    '''

    def decorator(func):
        func.query_params = query_params

        return func
    return decorator
