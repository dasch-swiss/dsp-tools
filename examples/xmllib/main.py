# noqa: INP001 (ignore add __init__.py)


from pathlib import Path

import pandas as pd

from dsp_tools import xmllib

data_folder = Path("examples/xmllib/data")


def _make_books(res_collection: xmllib.ResourceCollection) -> None:
    df = pd.read_csv(data_folder / "Book.csv")
    for _, row in df.iterrows():
        one_book = _make_one_book(row)
        res_collection.addResource(one_book)


def _make_one_book(row: pd.Series) -> xmllib.Resource:
    res = xmllib.Resource(res_id=row["id"], restype=":Book", label=row["label"])
    titles = row["hasTitle"].split("||")
    titles = [x.strip() for x in titles]
    res.addSeveralSimpleTexts(prop_name=":hasTitle", values=titles)
    res.addIntValue(prop_name=":hasNumberOfPages", value=row["hasNumberOfPages"])
    res.addSimpleText(prop_name=":hasAuthor", value=row["hasAuthor"])
    return res


def _make_chapters(res_collection: xmllib.ResourceCollection) -> None:
    df = pd.read_csv(data_folder / "Chapter.csv")
    for _, row in df.iterrows():
        one_chapter = _make_one_chapter(row)
        res_collection.addResource(one_chapter)


def _make_one_chapter(row: pd.Series) -> xmllib.Resource:
    res = xmllib.Resource(res_id=row["id"], restype=":Chapter", label=row["label"])
    res.addSimpleText(prop_name=":hasTitle", value=row["hasTitle"])
    res.addIntValue(prop_name=":hasChapterNumber", value=row["hasChapterNumber"])
    res.addLinkValue(prop_name=":isPartOfBook", value=row["isPartOfBook"])
    return res


def _add_images(res_collection: xmllib.ResourceCollection) -> None:
    files = [x for x in data_folder.glob("*.jpg")]
    for f in files:
        res_collection.addFileValueToResource(res_id=f.stem, filepath=str(f))


def main() -> None:
    """Creates an XML file from the csv files in the data folder."""
    resources = xmllib.ResourceCollection()
    _make_books(resources)
    _make_chapters(resources)
    _add_images(resources)
    root = xmllib.XMLRoot(shortcode="0001", default_ontology="onto", resource_collection=resources)
    root.write_file("examples/xmllib/data.xml")


if __name__ == "__main__":
    main()
