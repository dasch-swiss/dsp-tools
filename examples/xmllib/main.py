# noqa: INP001 (ignore add __init__.py)


from pathlib import Path

import pandas as pd

from dsp_tools import xmllib

data_folder = Path("examples/xmllib/data")


def _make_books(res_collection: xmllib.ResourceCollection) -> None:
    df = pd.read_csv(data_folder / "Book.csv")
    for _, row in df.iterrows():
        one_book = _make_one_book(row)
        res_collection.with_Resource(one_book)


def _make_one_book(row: pd.Series) -> xmllib.Resource:
    res = xmllib.Resource(res_id=row["id"], restype=":Book", label=row["label"])
    titles = row["hasTitle"].split("||")
    titles = [x.strip() for x in titles]
    res.with_SeveralSimpleTexts(
        prop_name=":hasTitle",
        values=titles,
    ).with_IntValue(
        prop_name=":hasNumberOfPages",
        value=row["hasNumberOfPages"],
    ).with_SimpleText(prop_name=":hasAuthor", value=row["hasAuthor"])
    return res


def _make_chapters(res_collection: xmllib.ResourceCollection) -> None:
    df = pd.read_csv(data_folder / "Chapter.csv")
    for _, row in df.iterrows():
        one_chapter = _make_one_chapter(row)
        res_collection.with_Resource(one_chapter)


def _make_one_chapter(row: pd.Series) -> xmllib.Resource:
    return (
        xmllib.Resource(
            res_id=row["id"],
            restype=":Chapter",
            label=row["label"],
        )
        .with_SimpleText(
            prop_name=":hasTitle",
            value=row["hasTitle"],
        )
        .with_IntValue(
            prop_name=":hasChapterNumber",
            value=row["hasChapterNumber"],
        )
        .with_LinkValue(prop_name=":isPartOfBook", value=row["isPartOfBook"])
    )


def _add_images(res_collection: xmllib.ResourceCollection) -> None:
    files = [x for x in data_folder.glob("*.jpg")]
    for f in files:
        res_collection.add_FileValueToResource(res_id=f.stem, filepath=str(f))


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
