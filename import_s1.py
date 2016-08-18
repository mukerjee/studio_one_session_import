#!/usr/bin/python

import sys
import os
from lxml import etree as ElementTree
import zipfile
import shutil

from song_model import SongModel


def import_tag(tag, src_tree, dst_tree):
    src_tag = src_tree.xpath(tag)[0]
    dst_tag = dst_tree.xpath(tag)[0]

    p = dst_tag.getparent()
    p.replace(dst_tag, src_tag)


def extract(prefix):
    f = zipfile.ZipFile(prefix + '.song', 'r')
    f.extractall(prefix)
    f.close()


def compress(prefix):
    f = zipfile.ZipFile(prefix + '-new.song', 'w', zipfile.ZIP_DEFLATED)
    os.chdir(prefix)
    for root, dirs, files in os.walk('./'):
        for file in files:
            f.write(os.path.join(root, file))
    f.close()
    os.chdir('../')


def delete_temp(prefix):
    shutil.rmtree(prefix)

from_prefix = os.path.splitext(sys.argv[1])[0]
to_prefix = os.path.splitext(sys.argv[2])[0]

extract(from_prefix)
extract(to_prefix)

src_song = SongModel(from_prefix)
print ElementTree.tostring(src_song.song.time_sig_map)

parser = ElementTree.XMLParser(recover=True)
dst_tree = ElementTree.fromstring(open(to_prefix + '/Song/song.xml').read(), parser)

# import_tag("////TempoMap", from_tree, to_tree)
# import_tag("////TimeSignatureMap", from_tree, to_tree)
# import_tag("////MarkerTrack", from_tree, to_tree)

# open(to_prefix + '/Song/song.xml', 'w').write(ElementTree.tostring(to_tree))

# compress(to_prefix)

# delete_temp(from_prefix)
# delete_temp(to_prefix)
