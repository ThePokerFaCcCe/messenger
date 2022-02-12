from core.utils import get_list_of_dict_values


def assert_items_are_same_as_data(items: list, data: list[dict], data_key='id'):
    """Finds all values of `data_key` in `data`, and 
    checks this values are same as `items` values"""

    data_items = get_list_of_dict_values(data, data_key)
    assert len(data_items) == len(items), (
        "items length isn't equal to found data items length"
    )

    assert all(item in data_items for item in items), (
        "items and found data items are not same"
    )
