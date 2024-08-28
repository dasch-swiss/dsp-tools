# noqa: INP001 (ignore add __init__.py)


from pathlib import Path

import pandas as pd

from dsp_tools import xmllib

data_folder = Path("examples/xmllib/data")


def _make_books() -> list[xmllib.Resource]:
    df = pd.read_csv(data_folder / "Book.csv")
    files = {x.stem: x for x in data_folder.glob("*.jpg")}
    books = []
    for _, row in df.iterrows():
        filename = files.get(row["id"])
        one_book = _make_one_book(row, filename)
        books.append(one_book)
    return books


def _make_one_book(row: pd.Series, filename: str | None) -> xmllib.Resource:
    titles = row["hasTitle"].split("||")
    titles = [x.strip() for x in titles]
    return (
        xmllib.Resource(res_id=row["id"], restype=":Book", label=row["label"])
        .add_simple_texts(prop_name=":hasTitle", values=titles)
        .add_integer(prop_name=":hasNumberOfPages", value=row["hasNumberOfPages"])
        .add_simple_text(prop_name=":hasAuthor", value=row["hasAuthor"])
        .add_file(filename=filename)
        .add_simple_text_optional(prop_name=":hasComment", value=row["hasComment"])
    )


def _make_chapters() -> list[xmllib.Resource]:
    df = pd.read_csv(data_folder / "Chapter.csv")
    chapters = []
    for _, row in df.iterrows():
        one_chapter = _make_one_chapter(row)
        chapters.append(one_chapter)
    return chapters


def _make_one_chapter(row: pd.Series) -> xmllib.Resource:
    return (
        xmllib.Resource(res_id=row["id"], restype=":Chapter", label=row["label"])
        .add_simple_text(prop_name=":hasTitle", value=row["hasTitle"])
        .add_integer(prop_name=":hasChapterNumber", value=row["hasChapterNumber"])
        .add_link(prop_name=":isPartOfBook", value=row["isPartOfBook"])
    )


def main() -> None:
    """Creates an XML file from the csv files in the data folder."""
    root = xmllib.XMLRoot(shortcode="0001", default_ontology="onto")

    books = _make_books()
    root = root.add_resources(books)

    chapters = _make_chapters()
    root = root.add_resources(chapters)

    root.write_file("examples/xmllib/data.xml")


if __name__ == "__main__":
    main()
