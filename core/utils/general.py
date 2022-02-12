def get_list_of_dict_values(data: list[dict], key) -> list:
    return [d.get(key) for d in data]
