from lxml import etree


def test_to_data_rdf(data_xml: etree._Element) -> None:
    res_list = list(data_xml.iterdescendants(tag="resource"))
    all_types = {x.attrib["restype"] for x in res_list}
    assert all_types == {
        "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#TestStillImageRepresentation",
        "http://0.0.0.0:3333/ontology/9999/second-onto/v2#SecondOntoClass",
    }
    expected_names = {
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testColor",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue",
        "http://0.0.0.0:3333/ontology/9999/second-onto/v2#testBoolean",
        "http://api.knora.org/ontology/knora-api/v2#hasColor",
        "http://api.knora.org/ontology/knora-api/v2#isRegionOf",
        "http://api.knora.org/ontology/knora-api/v2#hasGeometry",
        "http://api.knora.org/ontology/knora-api/v2#hasComment",
    }
    assert set(data_xml.xpath("//@name")) == expected_names
