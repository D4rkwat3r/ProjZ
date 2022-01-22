def freeze(entity: object):
    if isinstance(entity, dict):
        return frozenset((key, freeze(value)) for key, value in entity.items())
    elif isinstance(entity, list):
        return tuple(freeze(value) for value in entity)
    return entity