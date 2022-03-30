import json
from typing import Any, Union, cast, Optional
from lxml import etree
from enum import Enum
import csv2xml_helper_functions as csv2xml


allowed_resources = [
    'Resource'
    'StillImageRepresentation'
    'TextRepresentation'
    'AudioRepresentation'
    'DDDRepresentation'
    'DocumentRepresentation'
    'MovingImageRepresentation'
    'ArchiveRepresentation'
    'LinkObj'
]

allowed_properties = [
    'hasValue_TextValue',
    'hasValue_ColorValue',
    'hasValue_DateValue',
    'hasValue_TimeValue',
    'hasValue_DecimalValue',
    'hasValue_GeomValue',
    'hasValue_GeonameValue',
    'hasValue_IntValue',
    'hasValue_BooleanValue',
    'hasValue_UriValue',
    'hasValue_IntervalValue',
    'hasValue_ListValue',
    'hasColor',
    'hasComment',
    'hasLinkTo',
    'hasRepresentation'
]

multimedia_resclasses = [
    'StillImageRepresentation',
    'TextRepresentation',
    'AudioRepresentation',
    'DDDRepresentation',
    'DocumentRepresentation',
    'MovingImageRepresentation',
    'ArchiveRepresentation'
]

available_file_sizes = {
    '5KB': 5000,
    '10KB': 10000,
    '50KB': 50000,
    '100KB': 100000,
    '500KB': 500000,
    '1MB': 1000000,
    '5MB': 5000000,
    '10MB': 10000000,
    '50MB': 50000000,
    '100MB': 100000000,
}


class Defaults(Enum):
    identicalOntologiesDefault = 1

    r_inheritanceDepthDefault = 1
    classesPerInheritanceLevelDefault = 1
    classesPerInheritanceLevelMax = 10
    resourcesPerClassDefault = 10
    resourcesPerClassMax = 10000
    annotationsPerResourceDefault = 0
    annotationsPerResourceMax = 100
    regionsPerResourceDefault = 0
    regionsPerResourceMax = 100
    fileSizeDefault = 5000

    numOfValuesPerPropDefault = 1
    cardinalityDefault = '0-n'

    p_inheritanceDepthDefault = 1
    p_propertiesPerLevelDefault = 1

    permissionsDefault = {'res-default': ['V', 'V', 'CR', 'CR']}


def parse_lists() -> Optional[dict[str, Union[int, list[int]]]]:
    return None


def create_lists(numOfLists: int, numOfDepthLevels: int, nodesPerDepthLevel: list[int]) -> list[dict[Any, Any]]:
    pass
    # TODO


def parse_salsah_links() -> Optional[dict[str, Union[str, int, bool]]]:
    return None


def create_ontologies() -> list[dict[Any, Any]]:
    pass


def parse_cardinalities(cardinalities: Optional[dict[str, Union[int, dict[str, Any]]]], permissions: dict[str, list[str]]) -> dict[str, Any]:
    perm = next(iter(permissions.keys()))  # the first element (in insertion order)
    res: dict[str, dict[str, Any]] = dict()
    if cardinalities is None:
        pass
        #TODO
    else:
        for proptype, propdef in {k: v for k, v in cardinalities.items() if k in allowed_properties}.items():
            if isinstance(propdef, int):
                res[proptype] = {
                    'numOfProps': propdef,
                    'numOfValuesPerProp': [Defaults.numOfValuesPerPropDefault] * propdef,
                    'cardinality': [Defaults.cardinalityDefault] * propdef,
                    'permissions': [perm] * propdef
                }
            elif isinstance(propdef, dict):
                res[proptype] = propdef
            else:
                print('ERROR')
    return res


def validate_file_size_list(value: Optional[Union[str, list[str]]], length: int) -> list[int]:
    if value is None:
        new_value = [cast(int, Defaults.fileSizeDefault)] * length
    elif isinstance(value, str) and value in available_file_sizes:
        new_value = [available_file_sizes[value]] * length
    elif all([
        isinstance(value, list)
        and len(value) == length
        and all([elem in available_file_sizes for elem in value])
    ]):
        new_value = [available_file_sizes[elem] for elem in value]
    else:
        print('ERROR')
    return new_value


def validate_int_list(value: Optional[Union[int, list[int]]], maximum: int, default: int, length: int) -> list[int]:
    if value is None:
        new_value = [default] * length
    elif isinstance(value, int) and 1 <= value <= maximum:
        new_value = [value] * length
    elif all([
        isinstance(value, list)
        and len(value) == length
        and all([isinstance(elem, int) for elem in value])
        and all([1 <= elem <= 10 for elem in value])
    ]):
        new_value = cast(list[int], value)
    else:
        print('ERROR')
    return new_value


def parse_config_file(config: dict[Any, Any]) -> tuple[
    int,
    dict[str, dict[str, Any]],
    dict[str, dict[str, int]],
    Optional[dict[str, Union[int, list[int]]]],
    Optional[dict[str, Union[str, int, bool]]],
    dict[str, list[str]],
    bool
]:
    permissions = config.get('permissions', cast(dict[str, list[str]], Defaults.permissionsDefault))
    used_properties: set[str] = set()
    identicalOntologies: int = config.get('identicalOntologies', cast(int, Defaults.identicalOntologiesDefault))
    parsed_resources: dict[str, dict[str, Any]] = dict()
    for resname, resdef in config['resources'].items():
        if resname not in allowed_resources:
            print('ERROR')
        if resname == 'LinkObj':
            pass
            # TODO
        else:
            inh_depth: int = resdef.get('inheritanceDepth', Defaults.r_inheritanceDepthDefault)
            classes_per_level = validate_int_list(
                value=resdef.get('classesPerInheritanceLevel'),
                maximum=cast(int, Defaults.classesPerInheritanceLevelMax),
                default=cast(int, Defaults.classesPerInheritanceLevelDefault),
                length=inh_depth
            )
            res_per_class = validate_int_list(
                value=resdef.get('resourcesPerClass'),
                maximum=cast(int, Defaults.resourcesPerClassMax),
                default=cast(int, Defaults.resourcesPerClassDefault),
                length=inh_depth
            )
            ann_per_res = validate_int_list(
                value=resdef.get('annotationsPerResource'),
                maximum=cast(int, Defaults.annotationsPerResourceMax),
                default=cast(int, Defaults.annotationsPerResourceDefault),
                length=inh_depth
            )
            regions_per_res = None
            if resname == 'StillImageRepresentation':
                regions_per_res = validate_int_list(
                    value=resdef.get('regionsPerResource'),
                    maximum=cast(int, Defaults.regionsPerResourceMax),
                    default=cast(int, Defaults.regionsPerResourceDefault),
                    length=inh_depth
                )
            file_size = None
            if resname in multimedia_resclasses:
                file_size = validate_file_size_list(resdef.get('fileSize'), length=inh_depth)
            cardinalities = parse_cardinalities(resdef.get('cardinalities'), permissions)
            used_properties = used_properties | set(cardinalities.keys())
            # TODO: isCompoundedOf
            parsed_resources[resname] = {
                'inheritanceDepth': inh_depth,
                'classesPerInheritanceLevel': classes_per_level,
                'resourcesPerClass': res_per_class,
                'annotationsPerResource': ann_per_res,
                'cardinalities': cardinalities
            }
            if regions_per_res:
                parsed_resources[resname]['regionsPerResource'] = regions_per_res
            if file_size:
                parsed_resources[resname]['fileSize'] = file_size

    properties: dict[str, dict[str, int]] = dict()
    for prop in [prop for prop in used_properties if prop in allowed_properties]:
        if prop in config.get('properties', ['']):
            propdef: dict[str, int] = {
                'inheritanceDepth': config['properties'].get('inheritanceDepth',
                                                             cast(int, Defaults.p_inheritanceDepthDefault)),
                'propertiesPerLevel': config['properties'].get('propertiesPerLevel',
                                                               cast(int, Defaults.p_propertiesPerLevelDefault))
            }
            properties[prop] = propdef
        else:
            properties[prop] = {
                'inheritanceDepth': cast(int, Defaults.p_inheritanceDepthDefault),
                'propertiesPerLevel': cast(int, Defaults.p_propertiesPerLevelDefault)
            }

    lists = parse_lists()
    salsahLinks = parse_salsah_links()
    outputFiles = bool(config.get('outputFiles', 'false') == 'true')

    return identicalOntologies, parsed_resources, properties, lists, salsahLinks, permissions, outputFiles


def create_data_model(
    shortcode: str,
    shortname: str,
    lists: Optional[dict[str, Union[int, list[int]]]]
) -> dict[str, Any]:
    data_model: dict[str, Any] = {
        '$schema': 'https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json',
        'project': {
            'shortcode': shortcode,
            'shortname': shortname,
            'longname': 'A generated project',
            'groups': [
                {
                    'name': 'testproject-editors',
                    'selfjoin': False,
                    'status': True
                }
            ],
            'users': [
                {
                    'username': 'testprojectedit',
                    'email': 'testprojectedit@test.org',
                    'givenName': 'testproject-given',
                    'familyName': 'testproject-family',
                    'password': 'testproject1234',
                    'lang': 'de',
                    'groups': [
                        ':testproject-editors'
                    ],
                    'projects': [
                        ':admin'
                    ]
                }
            ],
        }
    }
    if lists:
        data_model['project']['lists'] = create_lists(
            numOfLists=cast(int, lists['numOfLists']),
            numOfDepthLevels=cast(int, lists['numOfDepthLevels']),
            nodesPerDepthLevel=cast(list[int], lists['nodesPerDepthLevel'])
        )
    data_model['project']['ontologies'] = create_ontologies()

    return data_model


def create_xml_file() -> etree._Element:
    root = csv2xml.make_root(shortcode=shortcode, default_ontology=default_ontology)
    root = csv2xml.append_permissions(root)
    return root


def create_configurable_test_data(config: dict[Any, Any]) -> None:
    # TODO: validate the config file
    identicalOntologies, resources, properties, lists, salsahLinks, \
    permissions, outputFiles = parse_config_file(config)

    shortcode = '0820'
    shortname = 'generatedTestProject'

    data_model = create_data_model(shortcode, shortname, lists)

    xml_file = create_xml_file()








    ############
    # write files
    ############
    with open('testproject.json', 'w', encoding='utf8') as outfile:
        json.dump(data_model, outfile, indent=4, ensure_ascii=False)
    
