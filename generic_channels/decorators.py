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

            "type" : int,

            # - OPTIONAL:

            "regex":r'^(*)$', 

            # A func that returns a value, if first element was `False`, means isn't valid value
            # and the second element will be shown as error. otherwise, second element will set as value
            "validator": function(Any, consumer) -> (bool, Any)

            "queryset" : User.objects.all(),

            #lookup for filtering queryset. default is `pk`
            "lookup" : "pk", 

            #Filter queryset by this values that exists in params
            "filter_depends" : ["chat_id",]
        },
        "chat_id": {"type" : int}
    }
    ```

    '''

    def decorator(func):
        func.query_params = query_params

        return func
    return decorator
