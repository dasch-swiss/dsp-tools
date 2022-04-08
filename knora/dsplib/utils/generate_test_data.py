import json
import os
from typing import Any, Union, cast, Optional, Iterable
from lxml import etree
import knora.dsplib.utils.generate_xml_helper_functions as xml_helper
import knora.dsplib.utils.generate_json_helper_functions as json_helper
from knora.dsplib.utils.onto_validate import validate_ontology
from knora.dsplib.utils.xml_upload import validate_xml_against_schema


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

defaults: dict[str, Union[int, str, list[str], dict[str, list[str]]]] = {
    'identicalOntologiesDefault': 1,

    'r_inheritanceDepthDefault': 1,
    'classesPerInheritanceLevelDefault': 1,
    'classesPerInheritanceLevelMax': 10,
    'resourcesPerClassDefault': 10,
    'resourcesPerClassMax': 10000,
    'annotationsPerResourceDefault': 0,
    'annotationsPerResourceMax': 100,
    'regionsPerResourceDefault': 0,
    'regionsPerResourceMax': 100,
    'fileSizeDefault': 5000,

    'numOfValuesPerPropDefault': 1,
    'cardinalityDefault': '0-n',

    'p_inheritanceDepthDefault': 1,
    'p_propertiesPerLevelDefault': 1,
    'p_gui_elements': ["SimpleText"],
    'p_hlist': 1,
    'p_hasLinkTo_object': 'Resource',

    'permissionsDefault': {'res-default': ['V', 'V', 'CR', 'CR']}
}


def parse_lists() -> Optional[dict[str, Union[int, list[int]]]]:
    return None


def create_lists(numOfLists: int, numOfDepthLevels: int, nodesPerDepthLevel: list[int]) -> list[dict[Any, Any]]:
    pass
    # TODO


def parse_salsah_links() -> Optional[dict[str, Union[str, int, bool]]]:
    return None


def infinite_generator(iterable: Iterable):
    while True:
        for it in iterable:
            yield it


def create_ontologies(
    onto_names: list[str],
    resources: dict[str, dict[str, Any]],
    properties: dict[str, dict[str, Union[int, list[str]]]]
) -> list[dict[Any, Any]]:
    finished_props: list[dict[str, Any]] = list()
    for propname, propdef in properties.items():
        num_of_props = int(propdef['inheritanceDepth']) * int(propdef['propertiesPerLevel'])
        propname_elems = propname.split('_')
        super = propname_elems[0]
        if len(propname_elems) > 1:
            objects = (x for x in [propname.split('_')[1]] * num_of_props)
        elif propname == 'hasRepresentation':
            objects = (x for x in ['Representation'] * num_of_props)
        elif propname != 'hasComment':
            objects = (x for x in propdef['objects'])
        gui_elements = infinite_generator(propdef['gui_elements'])

        for i in range(propdef['propertiesPerLevel']):
            finished_props.append(json_helper.make_property_class(
                name=f'{propname}_class_{i}',
                super=super,
                object=next(objects),
                gui_element=next(gui_elements),
                hlist=propdef.get('hlist')
            ))
            if int(propdef['inheritanceDepth']) > 1:
                for j in range(propdef['propertiesPerLevel']):
                    finished_props.append(json_helper.make_property_class(
                        name=f'{propname}_class_{i}_subclass_{j}',
                        super=f'{propname}_class_{i}',
                        object=next(objects),
                        gui_element=next(gui_elements),
                        hlist=propdef.get('hlist')
                    ))
                    if int(propdef['inheritanceDepth']) > 2:
                        for k in range(propdef['propertiesPerLevel']):
                            finished_props.append(json_helper.make_property_class(
                                name=f'{propname}_class_{i}_subclass_{j}_subclass_{k}',
                                super=f'{propname}_class_{i}_subclass_{j}',
                                object=next(objects),
                                gui_element=next(gui_elements),
                                hlist=propdef.get('hlist')
                            ))

    existing_propclasses = [prop['name'] for prop in finished_props]

    finished_res: list[dict[str, Any]] = list()
    for resname, resdef in resources.items():
        for i in range(resdef['classesPerInheritanceLevel']):
            finished_res.append(json_helper.make_resource_class(
                name=f'{resname}_class_{i}',
                super=resname,
                cardinalities=resdef['cardinalities'],
                existing_propclasses=existing_propclasses
            ))
            if resdef['inheritanceDepth'] > 1:
                for j in range(resdef['classesPerInheritanceLevel']):
                    finished_res.append(json_helper.make_resource_class(
                        name=f'{resname}_class_{i}_subclass_{j}',
                        super=f'{resname}_class_{i}',
                        cardinalities=resdef['cardinalities'],
                        existing_propclasses=existing_propclasses
                    ))
                    if resdef['inheritanceDepth'] > 2:
                        for k in range(resdef['classesPerInheritanceLevel']):
                            finished_res.append(json_helper.make_resource_class(
                                name=f'{resname}_class_{i}_subclass_{j}_subclass{k}',
                                super=f'{resname}_class_{i}_subclass_{j}',
                                cardinalities=resdef['cardinalities'],
                                existing_propclasses=existing_propclasses
                            ))

    result = list()
    for onto_name in onto_names:
        result.append({
            'name': onto_name,
            'label': onto_name,
            'properties': finished_props,
            'resources': finished_res
        })

    return result


def parse_cardinalities(cardinalities: Optional[dict[str, Union[int, dict[str, Any]]]], permissions: dict[str, list[str]]) -> dict[str, Any]:
    perm = next(iter(permissions.keys()))  # the first element (in insertion order)
    parsed_cards: dict[str, dict[str, Any]] = dict()
    if cardinalities is None:
        pass
        #TODO
    else:
        for proptype, propdef in {k: v for k, v in cardinalities.items() if k in allowed_properties}.items():
            if isinstance(propdef, int):
                parsed_cards[proptype] = {
                    'numOfProps': propdef,
                    'numOfValuesPerProp': [defaults['numOfValuesPerPropDefault']] * propdef,
                    'cardinality': [defaults['cardinalityDefault']] * propdef,
                    'permissions': [perm] * propdef
                }
            elif isinstance(propdef, dict):
                if not isinstance(propdef['numOfValuesPerProp'], list):
                    propdef['numOfValuesPerProp'] = [propdef['numOfValuesPerProp']] * int(propdef['numOfProps'])
                if not isinstance(propdef['cardinality'], list):
                    propdef['cardinality'] = [propdef['cardinality']] * int(propdef['numOfProps'])
                parsed_cards[proptype] = propdef
            else:
                raise Exception
    return parsed_cards


def validate_file_size_list(value: Optional[Union[str, list[str]]], length: int) -> list[int]:
    if value is None:
        new_value = [cast(int, defaults['fileSizeDefault'])] * length
    elif isinstance(value, str) and value in available_file_sizes:
        new_value = [available_file_sizes[value]] * length
    elif all([
        isinstance(value, list)
        and len(value) == length
        and all([elem in available_file_sizes for elem in value])
    ]):
        new_value = [available_file_sizes[elem] for elem in value]
    else:
        raise Exception
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
        raise Exception
    return new_value


def parse_config_file(config: str) -> tuple[
    int,
    dict[str, dict[str, Any]],
    dict[str, dict[str, int]],
    Optional[dict[str, Union[int, list[int]]]],
    Optional[dict[str, Union[str, int, bool]]],
    dict[str, list[str]],
    bool
]:
    with open(config) as f:
        config_dict = json.load(f)
    permissions = config_dict.get('permissions', cast(dict[str, list[str]], defaults['permissionsDefault']))
    used_properties: set[str] = set()
    identicalOntologies: int = config_dict.get('identicalOntologies', cast(int, defaults['identicalOntologiesDefault']))
    parsed_resources: dict[str, dict[str, Any]] = dict()
    for resname, resdef in config_dict['resources'].items():
        if resname not in allowed_resources:
            raise Exception
        if resname == 'LinkObj':
            pass
            # TODO
        else:
            inh_depth: int = resdef.get('inheritanceDepth', defaults['r_inheritanceDepthDefault'])
            classes_per_level = validate_int_list(
                value=resdef.get('classesPerInheritanceLevel'),
                maximum=cast(int, defaults['classesPerInheritanceLevelMax']),
                default=cast(int, defaults['classesPerInheritanceLevelDefault']),
                length=inh_depth
            )
            res_per_class = validate_int_list(
                value=resdef.get('resourcesPerClass'),
                maximum=cast(int, defaults['resourcesPerClassMax']),
                default=cast(int, defaults['resourcesPerClassDefault']),
                length=inh_depth
            )
            ann_per_res = validate_int_list(
                value=resdef.get('annotationsPerResource'),
                maximum=cast(int, defaults['annotationsPerResourceMax']),
                default=cast(int, defaults['annotationsPerResourceDefault']),
                length=inh_depth
            )
            regions_per_res = None
            if resname == 'StillImageRepresentation':
                regions_per_res = validate_int_list(
                    value=resdef.get('regionsPerResource'),
                    maximum=cast(int, defaults['regionsPerResourceMax']),
                    default=cast(int, defaults['regionsPerResourceDefault']),
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

    properties: dict[str, dict[str, Union[int, list[str]]]] = dict()
    for prop in [prop for prop in used_properties if prop in allowed_properties]:
        if prop in config_dict.get('properties', ['']):
            propdef: dict[str, Union[int, list[str]]] = {
                'inheritanceDepth': config_dict['properties'].get('inheritanceDepth', defaults['p_inheritanceDepthDefault']),
                'propertiesPerLevel': config_dict['properties'].get('propertiesPerLevel', defaults['p_propertiesPerLevelDefault']),
                'gui_elements': config_dict['properties'].get('gui_elements', defaults['p_gui_elements'])
            }
            if prop.split('_')[-1] == 'ListValue':
                propdef['hlist'] = config_dict['properties'].get('hlist', defaults['p_hlist'])
            num_of_props = int(propdef['inheritanceDepth']) * int(propdef['propertiesPerLevel'])
            if prop == 'hasLinkTo':
                propdef['objects'] = config_dict['properties'].get('objects', [defaults['p_hasLinkTo_object']] * num_of_props)
            properties[prop] = propdef
        else:
            properties[prop] = {
                'inheritanceDepth': cast(int, defaults['p_inheritanceDepthDefault']),
                'propertiesPerLevel': cast(int, defaults['p_propertiesPerLevelDefault']),
                'gui_elements': cast(list[str], defaults['p_gui_elements'])
            }

    lists = parse_lists()
    salsahLinks = parse_salsah_links()
    outputFiles = bool(config_dict.get('outputFiles', 'false') == 'true')

    return identicalOntologies, parsed_resources, properties, lists, salsahLinks, permissions, outputFiles


def create_data_model(
    shortcode: str,
    shortname: str,
    onto_names: list[str],
    lists: Optional[dict[str, Union[int, list[int]]]],
    resources: dict[str, dict[str, Any]],
    properties: dict[str, dict[str, int]]
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
    data_model['project']['ontologies'] = create_ontologies(onto_names, resources, properties)

    return data_model


def create_xml_file(shortcode: str, default_ontology: str, permissions: dict[str, list[str]]) -> etree.Element:
    root = xml_helper.make_root(shortcode=shortcode, default_ontology=default_ontology)
    root = xml_helper.append_permissions(root)
    return root


def generate_test_data(config: str) -> None:
    # TODO: validate the config file
    identicalOntologies, resources, properties, lists, salsahLinks, \
    permissions, outputFiles = parse_config_file(config)

    shortcode = '0820'
    shortname = 'generatedProject'
    onto_names = [f'{shortname}_onto_{i}' for i in range(identicalOntologies)]

    data_model = create_data_model(
        shortcode, shortname, onto_names, lists, resources, properties
    )
    if not validate_ontology(data_model):
        exit(1)

    # xml_files: list[etree.Element] = list()
    # for onto_name in onto_names:
    #     xml_file = create_xml_file(shortcode, onto_name, permissions)
    #     if not validate_xml_against_schema('path to xml file', 'knora/dsplib/schemas/data.xsd'):
    #         exit(1)
    #     xml_files.append(xml_file)

    # write files
    dirname = f'{shortcode}-{shortname}'
    os.makedirs(dirname)
    with open(f'{dirname}/{shortname}-ontologies.json', 'w', encoding='utf8') as outfile:
        json.dump(data_model, outfile, indent=4, ensure_ascii=False)
    for xml_file, onto_name in zip(xml_files, onto_names):
        etree.indent(xml_file, space='    ')
        xml_string = etree.tostring(xml_file, encoding='unicode', pretty_print=True)
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string
        xml_string = xml_string.replace('&lt;', '<')
        xml_string = xml_string.replace('&gt;', '>')
        with open(f'{dirname}/{onto_name}-data.xml', 'w', encoding='utf-8') as f:
            f.write(xml_string)
