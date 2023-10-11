import networkx as nx


def _create_weighted_dict(links_dic: dict[str, list[str]]) -> dict[str, list[dict[str, int]]]:
    return {resource: _calculate_weight_links(links) for resource, links in links_dic.items()}


def _calculate_weight_links(links_list: list[str]) -> list[dict[str, int]]:
    link_dict = {k: 0 for k in set(links_list)}
    for link in links_list:
        link_dict[link] += 1
    return [{k: v} for k, v in link_dict.items()]
