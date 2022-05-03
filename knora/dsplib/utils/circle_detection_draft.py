import json
import sys
from typing import Optional, List


class ResourceEntry:
    """
    this class represents a resource

    Attributes
    ----------

    name : str
        Name of the resource

    hasLinkToName : str
        Name of the hasLinkTo-property of the resource before from where this resource was "derived" from

    cardinality : str
        cardinality of property,e.g. 1, 0-n, 1-n etc.

    """
    _name: str
    _hasLinkToName: str
    _cardinality: str

    def __init__(self,
                 name: str,
                 hasLinkToName: Optional[str] = None,
                 cardinality: Optional[str] = None
                 ):
        self._name = name
        self._hasLinkToName = hasLinkToName
        self._cardinality = cardinality

    @property
    def name(self) -> str:
        return self._name

    @property
    def hasLinkToName(self) -> str:
        return self._hasLinkToName

    @property
    def cardinality(self) -> str:
        return self._cardinality

    @hasLinkToName.setter
    def hasLinkToName(self, value: str) -> None:
        self._hasLinkToName = value

    @cardinality.setter
    def cardinality(self, value: str) -> None:
        self._cardinality = value

    @property
    def out(self):
        out = "[" + self._name
        if self._hasLinkToName is not None:
            out += " " + self._hasLinkToName
        if self._cardinality is not None:
            out += " " + self._cardinality
        out += "]"
        return out


def hasCircle(single_path) -> bool:
    """checks if a circle exists
    a circle goes from A-B-A, but not from A-A
    """
    for number in range(0, len(single_path) - 1):
        entry = single_path[number]
        if contains_res_by_name(single_path=single_path, target_entry=entry, pos=number + 1):
            if number != len(single_path) - 2:
                # exclude circles like A-A, only include circles that have at least 2 different kind of elements like
                # A-B-A.
                return True
    else:
        return False


def load_ontology(path_json) -> dict:
    """load ontology as dict"""
    with open(path_json) as f:
        onto_json_str = f.read()
    return json.loads(onto_json_str)


def get_properties(data_model) -> List:
    """returns all properties of an ontology"""
    ontology = data_model['project']['ontologies']
    ontology_dict = ontology[0]
    return ontology_dict["properties"]


def get_resources(data_model) -> List:
    """returns all resources of an ontology"""
    ontology = data_model['project']['ontologies']
    ontology_dict = ontology[0]
    return ontology_dict["resources"]


def get_HasLinkTo_dict(properties) -> dict:
    """returns a dict, with all hasLinkTo-Properties and the respective resource name they are pointing to"""
    links: dict[str, str] = dict()
    for prop in properties:
        super_prop = prop["super"]
        if super_prop.__contains__("hasLinkTo"):
            object_prop = prop["object"]
            object_prop = object_prop[1:]
            name = prop["name"]
            links[name] = object_prop
    return links


def main(path_json):
    # 1. prepare
    data_model = load_ontology(path_json=path_json)
    properties = get_properties(data_model=data_model)
    resources = get_resources(data_model=data_model)
    links = get_HasLinkTo_dict(properties=properties)

    # 2. get circles
    paths: List = list(list(list()))
    for resource in resources:
        try:
            name = resource["name"]
            if not resourceExistsInPaths(name, paths):
                path_family = get_path_family(name=name, resources=resources, links=links)
                paths.append(path_family)
        except Exception as e:
            print(e)

    # 3. display result
    display_result(paths)


def resourceExistsInPaths(name, paths) -> bool:
    """check if we have already added the resource in question to paths."""
    for path_family in paths:
        for single_path in path_family:
            for entry in single_path:
                if name == entry.name:
                    return True
    else:
        return False


def display_result(paths):
    """filters results, displays only paths with circles"""
    for path_family in paths:
        print("::::")
        for single_path in path_family:
            if hasCircle(single_path):
                print("single path")
                print(out_path_list(single_path))


def get_path_family(name, resources, links) -> List:
    """returns a list of paths, which have all the same starting point e.g. A-B-C-J, A-D-E, A-F-G-H-I etc. (=path
    family) """
    # create a path(a path containing only the starting point)
    first_path = list()
    first_path.append(ResourceEntry(name=name))
    # create open_paths list
    open_paths: List = list()
    # append first_path to open_paths
    open_paths.append(first_path)
    # let's get all paths that have this path as starting point
    complete_paths = get_complete_path_family(open_paths, resources, links)
    return complete_paths


def get_properties_resource(resource) -> dict:
    """returns all the properties of a single resource with their respective cardinalities"""
    entries = dict()
    cardinalities = resource["cardinalities"]
    for entry in cardinalities:
        name = entry["propname"]
        name = name[1:]
        cardinality = entry["cardinality"]
        entries[name] = cardinality
    return entries


def get_links_single_resource(target_name, resources, links) -> dict:
    """returns every hasToLink and the respective cardinality of a single resource"""
    linked_resources_dict = dict()
    for resource in resources:
        name = resource["name"]
        if target_name == name:
            properties_resource = get_properties_resource(resource)
            for propname in properties_resource:
                if links.keys().__contains__(propname):
                    linked_object = links.get(propname)
                    cardinality = properties_resource[propname]
                    linked_resources_dict[linked_object] = propname, cardinality
            break
    return linked_resources_dict

def close_path(single_path, complete_paths, open_paths):
    """close a path by adding it to complete paths and removing from open paths"""
    complete_paths.append(single_path)
    open_paths.remove(single_path)


def get_next_path(old_single_path, open_paths) -> list:
    "returns a new path without the last resource that was added to the path list"
    single_path = list(old_single_path[:-1])
    open_paths.append(single_path)
    return single_path


def get_last_element(list_):
    """returns last element of a list"""
    return list_[-1]


def contains_res_by_name(single_path, target_entry, pos):
    """returns first occurrence of target_entry in a list from pos to the end of the list"""
    iterated_path = single_path[pos:]
    for entry in iterated_path:
        if entry.name == target_entry.name:
            return True
    else:
        return False


def out_path_list(path):
    """returns a path in one line"""
    oneline_ = "["
    for entry in path:
        oneline_ += entry.out + " "
    oneline_ += "]"
    return oneline_


def get_complete_path_family(open_paths, resources, links) -> List:
    """returns all paths which have the same starting point(=path family).

       open_paths:

       -open_paths is a list of paths that have the same starting point and which are not complete
          in the sense that their last element, their last resource(=open_paths(-1))
          a) has a link to next resource(s)
          b) doesn't go round in a circle
       -open_paths is updated in a while-loop until every path has no next resource or ends in a circle
       (then they are removed and added to complete_paths)
       -new paths are added to open_paths if the last resource in the path has multiple resources

       complete_paths:
       -paths that end in a circle or their last element doesn't have a link to a next resource are added to complete_paths
       -when the while loop ends every path that was part of open_paths in now added to complete_paths
    """
    complete_paths: List = list()
    number = 0
    while (len(open_paths) != 0):
        # adapt number to length of open_paths
        number = number % len(open_paths)
        # choose single path according to number
        single_path = open_paths[number]
        # get links of the last position in path
        last_resource = get_last_element(single_path)
        target_name = last_resource.name
        res_links = get_links_single_resource(target_name=target_name, resources=resources, links=links)
        # process res_links
        if res_links == 0:
            # res_links == 0 means: last resource has no links, so path has no more resources
            # close this path
            close_path(single_path, complete_paths, open_paths)
        else:
            # res_links != 0 means last resource has links, so path has more resources which have to be added
            count = 0
            for name_key in res_links:
                count += 1
                entry = res_links[name_key]
                new_entry = ResourceEntry(name=name_key, hasLinkToName=entry[0], cardinality=entry[1])
                if contains_res_by_name(single_path=single_path,target_entry=new_entry, pos=0):
                    # circle found
                    single_path.append(new_entry)
                    close_path(single_path, complete_paths, open_paths)
                else:
                    # no circle found
                    single_path.append(new_entry)
                # prepare new paths
                if len(res_links) > count:
                    single_path = get_next_path(old_single_path=single_path, open_paths=open_paths)
        number += 1

    return complete_paths


if __name__ == '__main__':
    path_json = "/Users/gregorbachmann/Desktop/biz_onto4circular.json"
    main(path_json)
