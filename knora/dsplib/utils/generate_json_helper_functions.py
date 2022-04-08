from typing import Any, Optional, Union


# "Resource": {
        #     "inheritanceDepth": 2,
        #     "classesPerInheritanceLevel": 2,
        #     "resourcesPerClass": 1,
        #     "cardinalities": {
        #         "hasValue_TextValue": {
        #             "numOfProps": x,
        #             "cardinality": "0-1|0-n|1|1-n" | ["0-1|0-n|1|1-n", ...],
        #         },
        #         "hasValue_TextValue": {
        #             "numOfProps": x,
        #             "cardinality": "0-1|0-n|1|1-n" | ["0-1|0-n|1|1-n", ...],
        #         }
        #     }
        # }

def make_resource_class(
    name: str,
    super: str,
    cardinalities: dict[str, dict[str, Union[str, list[str]]]],
    existing_propclasses: list[str]
) -> dict[str, Union[str, dict[str, str], list[dict[str, str]]]]:
    finished_cards: list[dict[str, str]] = list()
    for card_name, card_def in cardinalities.items():
        eligible_propclasses = (x for x in existing_propclasses if x.startswith(card_name))
        for i in range(int(card_def['numOfProps'])):
            finished_cards.append({
                'propname': f':{next(eligible_propclasses)}',
                'cardinality': card_def['cardinality'][i]
            })

    return {
        'name': name,
        'labels': {'en': name},
        'comments': {'en': name},
        'super': super,
        'cardinalities': finished_cards
    }


def make_property_class(
    name: str,
    super: str,
    object: str,
    gui_element: str,
    hlist: Optional[str]
):
    res = {
        'name': name,
        'super': [super],
        'object': object,
        'labels': {
            'en': name
        },
        'gui_element': gui_element
    }
    if hlist:
        res['gui_attributes'] = {'hlist': hlist}
