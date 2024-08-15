import datetime

from dsp_tools import excel2xml


def test_find_date_in_string_iso() -> None:
    """template: 2021-01-01"""
    assert excel2xml.find_date_in_string("x 1492-10-12, x") == "GREGORIAN:CE:1492-10-12:CE:1492-10-12"
    assert excel2xml.find_date_in_string("x 0476-09-04. x") == "GREGORIAN:CE:0476-09-04:CE:0476-09-04"
    assert excel2xml.find_date_in_string("x (0476-09-04) x") == "GREGORIAN:CE:0476-09-04:CE:0476-09-04"
    assert excel2xml.find_date_in_string("x [1492-10-32?] x") is None


def test_find_date_in_string_eur_date() -> None:
    """template: 31.4.2021 | 5/11/2021 | 2015_01_02"""
    assert excel2xml.find_date_in_string("x (30.4.2021) x") == "GREGORIAN:CE:2021-04-30:CE:2021-04-30"
    assert excel2xml.find_date_in_string("x (5/11/2021) x") == "GREGORIAN:CE:2021-11-05:CE:2021-11-05"
    assert excel2xml.find_date_in_string("x ...2193_01_26... x") == "GREGORIAN:CE:2193-01-26:CE:2193-01-26"
    assert excel2xml.find_date_in_string("x -2193_01_26- x") == "GREGORIAN:CE:2193-01-26:CE:2193-01-26"
    assert excel2xml.find_date_in_string("x 2193_02_30 x") is None


def test_find_date_in_string_eur_date_2_digit() -> None:
    cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
    nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
    assert excel2xml.find_date_in_string(f"x 30.4.{cur} x") == f"GREGORIAN:CE:20{cur}-04-30:CE:20{cur}-04-30"
    assert excel2xml.find_date_in_string(f"x 30.4.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-30:CE:19{nxt}-04-30"
    assert excel2xml.find_date_in_string(f"x 31.4.{nxt} x") is None


def test_find_date_in_string_eur_date_range() -> None:
    """template: 27.-28.1.1900"""
    assert excel2xml.find_date_in_string("x 25.-26.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-26"
    assert excel2xml.find_date_in_string("x 25. - 26.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-26"
    assert excel2xml.find_date_in_string("x 25.-25.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-25"
    assert excel2xml.find_date_in_string("x 25.-24.2.0800 x") is None


def test_find_date_in_string_eur_date_range_2_digit() -> None:
    cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
    nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
    assert excel2xml.find_date_in_string(f"x 15.-16.4.{cur} x") == f"GREGORIAN:CE:20{cur}-04-15:CE:20{cur}-04-16"
    assert excel2xml.find_date_in_string(f"x 15.-16.4.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:19{nxt}-04-16"


def test_find_date_in_string_eur_date_range_across_month() -> None:
    """template: 26.2.-24.3.1948"""
    assert excel2xml.find_date_in_string("x _1.3. - 25.4.2022_ x") == "GREGORIAN:CE:2022-03-01:CE:2022-04-25"
    assert excel2xml.find_date_in_string("x (01.03. - 25.04.2022) x") == "GREGORIAN:CE:2022-03-01:CE:2022-04-25"
    assert excel2xml.find_date_in_string("x 28.2.-1.12.1515 x") == "GREGORIAN:CE:1515-02-28:CE:1515-12-01"
    assert excel2xml.find_date_in_string("x 28.2.-28.2.1515 x") == "GREGORIAN:CE:1515-02-28:CE:1515-02-28"
    assert excel2xml.find_date_in_string("x 28.2.-26.2.1515 x") is None


def test_find_date_in_string_eur_date_range_across_month_2_digit() -> None:
    cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
    nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
    assert excel2xml.find_date_in_string(f"x 15.04.-1.5.{cur} x") == f"GREGORIAN:CE:20{cur}-04-15:CE:20{cur}-05-01"
    assert excel2xml.find_date_in_string(f"x 15.04.-1.5.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:19{nxt}-05-01"


def test_find_date_in_string_eur_date_range_across_year() -> None:
    """template: 1.12.1973 - 6.1.1974"""
    assert excel2xml.find_date_in_string("x 1.9.2022-3.1.2024 x") == "GREGORIAN:CE:2022-09-01:CE:2024-01-03"
    assert excel2xml.find_date_in_string("x 25.12.2022 - 3.1.2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
    assert excel2xml.find_date_in_string("x 25/12/2022-03/01/2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
    assert excel2xml.find_date_in_string("x 25/12/2022 - 3/1/2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
    assert excel2xml.find_date_in_string("x 25.12.2022-25.12.2022 x") == "GREGORIAN:CE:2022-12-25:CE:2022-12-25"
    assert excel2xml.find_date_in_string("x 25/12/2022-25/12/2022 x") == "GREGORIAN:CE:2022-12-25:CE:2022-12-25"
    assert excel2xml.find_date_in_string("x 25.12.2022-03.01.2022 x") is None
    assert excel2xml.find_date_in_string("x 25/12/2022-03/01/2022 x") is None


def test_find_date_in_string_eur_date_range_across_year_2_digit() -> None:
    cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
    nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
    assert excel2xml.find_date_in_string(f"x 15.04.23-1.5.{cur} x") == f"GREGORIAN:CE:2023-04-15:CE:20{cur}-05-01"
    assert excel2xml.find_date_in_string(f"x 15.04.{nxt}-1.5.26 x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:1926-05-01"


def test_find_date_in_string_monthname() -> None:
    """template: February 9, 1908 | Dec 5,1908"""
    assert excel2xml.find_date_in_string("x Jan 26, 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
    assert excel2xml.find_date_in_string("x February26,2051 x") == "GREGORIAN:CE:2051-02-26:CE:2051-02-26"
    assert excel2xml.find_date_in_string("x Sept 1, 1000 x") == "GREGORIAN:CE:1000-09-01:CE:1000-09-01"
    assert excel2xml.find_date_in_string("x October 01, 1000 x") == "GREGORIAN:CE:1000-10-01:CE:1000-10-01"
    assert excel2xml.find_date_in_string("x Nov 6,1000 x") == "GREGORIAN:CE:1000-11-06:CE:1000-11-06"


def test_find_date_in_string_single_year() -> None:
    """template: 1907 | 476"""
    assert excel2xml.find_date_in_string("Text 1848 text") == "GREGORIAN:CE:1848:CE:1848"
    assert excel2xml.find_date_in_string("Text 0476 text") == "GREGORIAN:CE:476:CE:476"
    assert excel2xml.find_date_in_string("Text 476 text") == "GREGORIAN:CE:476:CE:476"


def test_find_date_in_string_year_range() -> None:
    """template: 1849/50 | 1845-50 | 1849/1850"""
    assert excel2xml.find_date_in_string("x 1849/1850? x") == "GREGORIAN:CE:1849:CE:1850"
    assert excel2xml.find_date_in_string("x 1845-1850, x") == "GREGORIAN:CE:1845:CE:1850"
    assert excel2xml.find_date_in_string("x 800-900, x") == "GREGORIAN:CE:800:CE:900"
    assert excel2xml.find_date_in_string("x 840-50, x") == "GREGORIAN:CE:840:CE:850"
    assert excel2xml.find_date_in_string("x 844-8, x") == "GREGORIAN:CE:844:CE:848"
    assert excel2xml.find_date_in_string("x 1840-1, x") == "GREGORIAN:CE:1840:CE:1841"
    assert excel2xml.find_date_in_string("x 0750-0760 x") == "GREGORIAN:CE:750:CE:760"
    assert excel2xml.find_date_in_string("x 1849/50. x") == "GREGORIAN:CE:1849:CE:1850"
    assert excel2xml.find_date_in_string("x (1845-50) x") == "GREGORIAN:CE:1845:CE:1850"
    assert excel2xml.find_date_in_string("x [1849/1850] x") == "GREGORIAN:CE:1849:CE:1850"
    assert excel2xml.find_date_in_string("x 1850-1849 x") is None
    assert excel2xml.find_date_in_string("x 1850-1850 x") is None
    assert excel2xml.find_date_in_string("x 830-20 x") is None
    assert excel2xml.find_date_in_string("x 830-30 x") is None
    assert excel2xml.find_date_in_string("x 1811-10 x") is None
    assert excel2xml.find_date_in_string("x 1811-11 x") is None
    assert excel2xml.find_date_in_string("x 1811/10 x") is None
    assert excel2xml.find_date_in_string("x 1811/11 x") is None


def test_find_date_in_string_french_bc() -> None:
    assert excel2xml.find_date_in_string("Text 12345 av. J.-C. text") == "GREGORIAN:BC:12345:BC:12345"
    assert excel2xml.find_date_in_string("Text 2000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:2000"
    assert excel2xml.find_date_in_string("Text 250 av. J.-C. text") == "GREGORIAN:BC:250:BC:250"
    assert excel2xml.find_date_in_string("Text 33 av. J.-C. text") == "GREGORIAN:BC:33:BC:33"
    assert excel2xml.find_date_in_string("Text 1 av. J.-C. text") == "GREGORIAN:BC:1:BC:1"


def test_find_date_in_string_french_bc_ranges() -> None:
    assert excel2xml.find_date_in_string("Text 99999-1000 av. J.-C. text") == "GREGORIAN:BC:99999:BC:1000"
    assert excel2xml.find_date_in_string("Text 1125-1050 av. J.-C. text") == "GREGORIAN:BC:1125:BC:1050"
    assert excel2xml.find_date_in_string("Text 1234-987 av. J.-C. text") == "GREGORIAN:BC:1234:BC:987"
    assert excel2xml.find_date_in_string("Text 350-340 av. J.-C. text") == "GREGORIAN:BC:350:BC:340"
    assert excel2xml.find_date_in_string("Text 842-98 av. J.-C. text") == "GREGORIAN:BC:842:BC:98"
    assert excel2xml.find_date_in_string("Text 45-26 av. J.-C. text") == "GREGORIAN:BC:45:BC:26"
    assert excel2xml.find_date_in_string("Text 53-7 av. J.-C. text") == "GREGORIAN:BC:53:BC:7"
    assert excel2xml.find_date_in_string("Text 6-5 av. J.-C. text") == "GREGORIAN:BC:6:BC:5"


def test_find_date_in_string_french_bc_orthographical_variants() -> None:
    assert excel2xml.find_date_in_string("Text 1 av. J.-C. text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av J.-C. text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av.J.-C. text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av. J.C. text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av. J-C text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av.JC text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av JC text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av. J.-C.text") == "GREGORIAN:BC:1:BC:1"


def test_find_date_in_string_french_bc_dash_variants() -> None:
    assert excel2xml.find_date_in_string("Text 2000-1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
    assert excel2xml.find_date_in_string("Text 2000- 1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
    assert excel2xml.find_date_in_string("Text 2000 -1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
    assert excel2xml.find_date_in_string("Text 2000 - 1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"


def test_find_date_in_string_french_bc_invalid_syntax() -> None:
    assert excel2xml.find_date_in_string("Text12 av. J.-C. text") is None
    assert excel2xml.find_date_in_string("Text 12 av. J.-Ctext") is None
    assert excel2xml.find_date_in_string("Text 1 avJC text") is None


def test_find_date_in_string_french_bc_invalid_range() -> None:
    assert excel2xml.find_date_in_string("Text 12-20 av. J.-C. text") is None
