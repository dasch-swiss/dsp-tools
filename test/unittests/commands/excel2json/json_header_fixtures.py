from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def prefixes_good() -> pd.DataFrame:
    return pd.DataFrame(
        {"prefixes": ["foaf:", "sdh"], "uri": ["http://xmlns.com/foaf/0.1/", "https://ontome.net/ns/sdhss/"]}
    )


@pytest.fixture
def prefixes_missing_col() -> pd.DataFrame:
    return pd.DataFrame({"uri": ["http://xmlns.com/foaf/0.1/", "https://ontome.net/ns/sdhss/"]})


@pytest.fixture
def prefixes_missing_val() -> pd.DataFrame:
    return pd.DataFrame(
        {"prefixes": ["foaf:", pd.NA], "uri": ["http://xmlns.com/foaf/0.1/", "https://ontome.net/ns/sdhss/"]}
    )


@pytest.fixture
def prefixes_wrong_val() -> pd.DataFrame:
    return pd.DataFrame({"prefixes": ["foaf:", "sdh"], "uri": ["http://xmlns.com/foaf/0.1/", "not a uri"]})


@pytest.fixture
def licenses_good() -> pd.DataFrame:
    return pd.DataFrame({"enabled": ["http://rdfh.ch/licenses/cc-by-4.0", "http://rdfh.ch/licenses/ai-generated"]})


@pytest.fixture
def project_good_missing_zero() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": [11], "shortname": ["name"], "longname": ["long"]})


@pytest.fixture
def project_good_no_zero() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": [1111], "shortname": ["name"], "longname": ["long"]})


@pytest.fixture
def project_missing_col() -> pd.DataFrame:
    return pd.DataFrame({"shortname": ["name"], "longname": ["long"]})


@pytest.fixture
def project_missing_val() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": [pd.NA], "shortname": ["name"], "longname": ["long"]})


@pytest.fixture
def project_too_many_rows() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": [11, 0], "shortname": ["name", pd.NA], "longname": ["long", "other"]})


@pytest.fixture
def description_good() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "description_en": ["english"],
            "description_de": [pd.NA],
            "fr": ["french"],
            "description_rm": [pd.NA],
        }
    )


@pytest.fixture
def description_too_many_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "description_en": ["english", "en1"],
            "description_de": [pd.NA, pd.NA],
            "fr": ["french", "french2"],
            "description_it": [pd.NA, "it"],
            "description_rm": [pd.NA, pd.NA],
        }
    )


@pytest.fixture
def description_missing_col() -> pd.DataFrame:
    return pd.DataFrame({"other": ["english"]})


@pytest.fixture
def description_missing_val() -> pd.DataFrame:
    return pd.DataFrame({"other": ["english"], "description_en": [pd.NA]})


@pytest.fixture
def keywords_good() -> pd.DataFrame:
    return pd.DataFrame({"keywords": ["one", pd.NA, "three"]})


@pytest.fixture
def keywords_missing_col() -> pd.DataFrame:
    return pd.DataFrame({"other": [1]})


@pytest.fixture
def keywords_missing_val() -> pd.DataFrame:
    return pd.DataFrame({"other": [1], "keywords": [pd.NA]})


@pytest.fixture
def users_good() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": ["Alice", "Caterpillar", "WhiteRabbit"],
            "email": ["alice@dasch.swiss", "caterpillar@dasch.swiss", "white.rabbit@dasch.swiss"],
            "givenname": ["Alice Pleasance", "Caterpillar", "White"],
            "familyname": ["Liddell", "Wonderland", "Rabbit"],
            "password": ["alice4322", "alice7652", "alice8711"],
            "lang": ["en", "de", "fr"],
            "role": ["systemadmin", "projectadmin", "projectmember"],
        }
    )


@pytest.fixture
def users_missing_col() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": ["Alice"],
            "email": ["alice@dasch.swiss"],
            "givenname": ["Alice Pleasance"],
            "familyname": ["Liddell"],
            "lang": ["fr"],
            "role": ["systemadmin"],
        }
    )


@pytest.fixture
def users_missing_val() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": [pd.NA],
            "email": ["alice@dasch.swiss"],
            "givenname": ["Alice Pleasance"],
            "familyname": ["Liddell"],
            "password": ["alice7652"],
            "lang": ["fr"],
            "role": ["systemadmin"],
        }
    )


@pytest.fixture
def users_wrong_lang() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": ["Alice"],
            "email": ["alice@dasch.swiss"],
            "givenname": ["Alice Pleasance"],
            "familyname": ["Liddell"],
            "password": ["alice7652"],
            "lang": ["other"],
            "role": ["systemadmin"],
        }
    )


@pytest.fixture
def user_good() -> pd.Series[str]:
    return pd.Series(
        {
            "username": "Alice",
            "email": "alice@dasch.swiss",
            "givenname": "Alice Pleasance",
            "familyname": "Liddell",
            "password": "alice7652",
            "lang": "en",
            "role": "systemadmin",
        }
    )


@pytest.fixture
def user_wrong_lang() -> pd.Series[str]:
    return pd.Series(
        {
            "username": "Alice",
            "email": "alice@dasch.swiss",
            "givenname": "Alice Pleasance",
            "familyname": "Liddell",
            "password": "alice7652",
            "lang": "other",
            "role": "systemadmin",
        }
    )


@pytest.fixture
def user_wrong_email() -> pd.Series[str]:
    return pd.Series(
        {
            "username": "Alice",
            "email": "not an email",
            "givenname": "Alice Pleasance",
            "familyname": "Liddell",
            "password": "alice7652",
            "lang": "fr",
            "role": "systemadmin",
        }
    )


@pytest.fixture
def user_wrong_role() -> pd.Series[str]:
    return pd.Series(
        {
            "username": "Alice",
            "email": "alice@dasch.swiss",
            "givenname": "Alice Pleasance",
            "familyname": "Liddell",
            "password": "alice7652",
            "lang": "fr",
            "role": "other",
        }
    )
