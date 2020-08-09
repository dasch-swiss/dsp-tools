
def setAttribute(self, name, val):
    super().__setattr__(name, val)

def init(self):
    print('in __init__')

def getter(self):
    return self._gaga

def setter(self,value):
    self._gaga = value

gaga = {}
gaga['TestClass'] = type('TestClass', (), {
    '__init__': init,
    'set_gaga': setter,
    'gaga': property(getter, setter)
})

t = gaga['TestClass']
t.gaga = 'GAGAGA'
print(t.gaga)

class A:
    a: str

    class B:
        b: str

        def __init__(self):
            self.b = 'B'

        def doB(self):
            print('-->doB ' + self.b + ' ' + A.a)

    def __init__(self):
        self.a = 'A'

    def doA(self):
        print('-->doA ' + self.a)
        self.bb = self.B()
        self.bb.doB()


gaga = A()
gaga.doA()

