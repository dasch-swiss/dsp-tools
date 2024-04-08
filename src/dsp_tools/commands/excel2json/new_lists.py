import pandas as pd

from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.utils.shared import simplify_name


def _make_single_node(node_series: pd.Series, depth_number: int) -> ListNode:
    cols = [x for x in node_series.index if x.endswith(f"_{depth_number}")]
    labels = {x.rstrip(f"_{depth_number}"): node_series[x] for x in cols}
    return ListNode(node_series.get("ID (optional)"), labels)


def _fill_ids(df: pd.DataFrame) -> pd.DataFrame:
    df["ID (optional)"] = df["ID (optional)"].fillna(df["en"].apply(simplify_name))
    return df
