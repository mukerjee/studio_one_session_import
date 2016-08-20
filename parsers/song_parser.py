from lxml import etree as ElementTree


class Parser(object):
    def __init__(self, fn):
        self.fn = fn
        xml = open(fn).read()
        xml = xml.split('\n')
        xml[1] = xml[1].split('>')[0] + ' xmlns:x="x">'
        xml = '\n'.join(xml)
        self.tree = ElementTree.fromstring(xml)
        self.ns = {'x': 'x'}

    def write(self):
        open(self.fn, 'w').write(ElementTree.tostring(self.tree))

    def swap(self, old, new):
        p = old.getparent()
        p.replace(old, new)

    def fix_uid(self, uid):
        return '{%s-%s-%s-%s-%s}' % (uid[:8], uid[8:12],
                                     uid[12:16], uid[16:20], uid[20:])

