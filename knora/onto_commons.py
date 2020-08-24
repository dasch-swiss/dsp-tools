import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
import sys
import re

from knora.models.helpers import Actions, BaseError, Context, Cardinality
from knora.models.langstring import Languages, LangStringParam, LangString
from knora.models.connection import Connection, Error
from knora.models.project import Project
from knora.models.listnode import ListNode
from knora.models.group import Group
from knora.models.user import User
from knora.models.ontology import Ontology
from knora.models.propertyclass import PropertyClass
from knora.models.resourceclass import ResourceClass

def list_creator(con: Connection, project: Project, parent_node: ListNode, nodes: List[dict]):
    nodelist = []
    for node in nodes:
        newnode = ListNode(
            con=con,
            project=project,
            label=node["labels"],
            comment=node.get("comments"),
            name=node["name"],
            parent=parent_node
        ).create()
        if node.get('nodes') is not None:
            subnodelist = list_creator(con, project, newnode, node['nodes'])
            nodelist.append({newnode.name: {"id": newnode.id, 'nodes': subnodelist}})
        else:
            nodelist.append({newnode.name: {"id": newnode.id}})
    return nodelist

