from lxml import etree as ElementTree


class Parser(object):
    fn = None
    tree = None

    def __init__(self, fn):
        self.fn = fn
        parser = ElementTree.XMLParser(recover=True)
        self.tree = ElementTree.fromstring(open(fn).read(), parser)

    def write(self):
        open(self.fn, 'w').write(ElementTree.tostring(self.tree))
