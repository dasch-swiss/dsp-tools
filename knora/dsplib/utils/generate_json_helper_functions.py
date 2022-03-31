from typing import Any


def make_resource(resource_def: dict[str, Any]):

    return {
        'name': name,
        'labels': {'en': name},
        'comments': {'en': name},
        'super': 'Resource',
        'cardinalities':
    }
