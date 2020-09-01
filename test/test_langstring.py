import unittest

from dsplib.models.langstring import Languages, LangStringParam, LangString


class TestLangString(unittest.TestCase):

    def test_langstring_instantiation1(self):
        """Test a LangString without language."""
        ls = LangString('Ein simpler String')
        self.assertEqual(ls[None], 'Ein simpler String')

    def test_langstring_instantiation2(self):
        """Test a LangString using string and Languages-enums as index."""
        ls = LangString({'de': 'Ein simpler String', 'fr': 'Quelque chose en français'})
        self.assertEqual(ls['de'], 'Ein simpler String')
        self.assertEqual(ls[Languages.FR], 'Quelque chose en français')

    def test_langstring_instantiation3(self):
        """Test a LangString using string and Languages-enums as index."""
        ls = LangString({Languages.DE: 'Ein simpler String', Languages.FR: 'Quelque chose en français'})
        self.assertEqual(ls[Languages.DE], 'Ein simpler String')
        self.assertEqual(ls['fr'], 'Quelque chose en français')

    def test_langstring_change(self):
        """test if changing a LangString item works."""
        ls = LangString({Languages.DE: 'Ein simpler String', Languages.FR: 'Quelque chose en français'})
        ls['de'] = 'gagaga'
        self.assertEqual(ls[Languages.DE], 'gagaga')
        self.assertEqual(ls['fr'], 'Quelque chose en français')

    def test_langstring_fromjson(self):
        """Test reading a LangString from JSON as used in Knora Admin."""
        test = [{
            'language': 'en',
            'value': 'This is a test'
        }, {
            'language': 'de',
            'value': 'Das ist ein Test'
        }]
        ls = LangString.fromJsonObj(test)
        self.assertEqual(ls['de'], 'Das ist ein Test')
        self.assertEqual(ls[Languages.EN], 'This is a test')

    def test_langstring_fromjsonld(self):
        """Test reading a LangString from JSON-LD as used in Knora data/ontologies"""
        test = [{
            '@language': 'en',
            '@value': 'This is a test'
        }, {
            '@language': 'de',
            '@value': 'Das ist ein Test'
        }]
        ls = LangString.fromJsonLdObj(test)
        self.assertEqual(ls['de'], 'Das ist ein Test')
        self.assertEqual(ls[Languages.EN], 'This is a test')

    def test_langstring_tojson(self):
        """Test converting a LangString to JSON and JSON-LD"""
        ls = LangString('Ein simpler String')
        json = ls.toJsonObj()
        self.assertEqual(json, 'Ein simpler String')
        json = ls.toJsonLdObj()
        self.assertEqual(json, 'Ein simpler String')

        ls = LangString({Languages.DE: 'Ein simpler String', Languages.FR: 'Quelque chose en français'})
        json = ls.toJsonObj()
        expected = [{'language': 'de',
                     'value': 'Ein simpler String'},
                    {'language': 'fr',
                     'value': 'Quelque chose en français'}]
        self.assertEqual(json, expected)
        jsonld = ls.toJsonLdObj()
        expected = [{'@language': 'de',
                     '@value': 'Ein simpler String'},
                    {'@language': 'fr',
                     '@value': 'Quelque chose en français'}]
        self.assertEqual(jsonld, expected)

    def test_langstring_emptyness(self):
        """Test if a LanGstring can be emptied and if the emptyness is detected."""
        ls = LangString()
        self.assertTrue(ls.isEmpty())
        ls = LangString('Ein simpler String')
        ls.empty()
        self.assertTrue(ls.isEmpty())
        ls = LangString({Languages.DE: 'Ein simpler String', Languages.FR: 'Quelque chose en français'})
        ls.empty()
        self.assertTrue(ls.isEmpty())

    def test_langstring_iterator(self):
        """Test iterating over a LangString."""
        ls = LangString({Languages.DE: 'Ein simpler String', Languages.FR: 'Quelque chose en français'})
        for tmp in ls:
            if tmp[0] == Languages.DE:
                self.assertEqual(tmp[1], 'Ein simpler String')
            elif tmp[0] == Languages.FR:
                self.assertEqual(tmp[1], 'Quelque chose en français')


if __name__ == '__main__':
    unittest.main()
