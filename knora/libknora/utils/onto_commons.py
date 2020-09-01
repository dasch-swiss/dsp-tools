from typing import List, Set, Dict, Tuple, Optional

from ..models.connection import Connection
from ..models.project import Project
from ..models.listnode import ListNode

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

