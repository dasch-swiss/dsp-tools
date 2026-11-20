from dsp_tools.commands.excel2xml.excel2xml_lib import _escape_reserved_chars


class TestEscapedChars:
    def test_single_br(self) -> None:
        test_text = "Text <br/> text after"
        res = _escape_reserved_chars(test_text)
        assert res == test_text

    def test_single_br_with_other(self) -> None:
        test_text = "Text <br/>> text after"
        expected = "Text <br/>&gt; text after"
        res = _escape_reserved_chars(test_text)
        assert res == expected

    def test_wrong_single_br(self) -> None:
        test_text = "Text <br//> text after"
        expected = "Text &lt;br//&gt; text after"
        res = _escape_reserved_chars(test_text)
        assert res == expected

    def test_emphasis(self) -> None:
        test_text = "Text before [<em>emphasis</em>] Text after illegal amp: &"
        expected = "Text before [<em>emphasis</em>] Text after illegal amp: &amp;"
        res = _escape_reserved_chars(test_text)
        assert res == expected

    def test_link(self) -> None:
        test_text = 'Before <a class="salsah-link" href="IRI:link:IRI">link</a> after'
        res = _escape_reserved_chars(test_text)
        assert res == test_text

    def test_illegal_angular(self) -> None:
        test_text = "Before <TagNotKnown>in tags</TagNotKnown> After."
        expected = "Before &lt;TagNotKnown&gt;in tags&lt;/TagNotKnown&gt; After."
        res = _escape_reserved_chars(test_text)
        assert res == expected
