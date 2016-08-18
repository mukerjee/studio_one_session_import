from lxml import etree as ElementTree


class Parser(object):
    def __init__(self, fn):
        self.fn = fn
        parser = ElementTree.XMLParser(recover=True)
        self.tree = ElementTree.fromstring(open(fn).read(), parser)

    def write(self):
        open(self.fn, 'w').write(ElementTree.tostring(self.tree))

    def swap(self, old, new):
        p = old.getparent()
        p.replace(old, new)

    def add_sibling(self, olds_dict, new):
        p = olds_dict.values()[0].getparent()
        p.append(new)
