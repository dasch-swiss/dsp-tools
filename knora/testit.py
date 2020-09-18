import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from dsplib.models.connection import Connection
from dsplib.models.resource import ResourceInstanceFactory
from dsplib.models.value import BooleanValue, ColorValue, DateValue, DecimalValue, IntValue, IntervalValue, TextValue, \
    UriValue, KnoraStandoffXml
from pprint import pprint

con = Connection('http://0.0.0.0:3333')
con.login('root@example.com', 'test')
factory = ResourceInstanceFactory(con, 'anything')
resclassnames = factory.get_resclass_names()

BlueThing = factory.get_resclass('anything:BlueThing')
a_blue_thing = BlueThing(con=con,
                         label='BlueThing',
                         values={
                            'anythinghas:Boolean': True,
                            'anything:hasColor': ['#ff0033', '#0077FF'],
                            'anything:hasDate': ('1833', 'not verified!'),
                            'anything:hasDecimal': 3.14159,
                            'anything:hasInteger': "42",
                            'anything:hasInterval': [("0.0:3.0", "first interval"), ("3.5:3.7", "second interval")],
                            'anything:hasRichtext': KnoraStandoffXml("This is <b>bold</b> text."),
                            'anything:hasText': "Dies ist ein einfacher Text",
                            'anything:hasUri': 'http://gaga.com'
                         }).create()
for resclassname in resclassnames:
#    print('=======>', resclassname)
#    RC = factory.get_resclass(resclassname)
#    gaga = RC(con=con, label='TEST')
#    #gaga.create()

