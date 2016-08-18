#!/usr/bin/python

import sys
from song_parser import Parser


class MediaPool(Parser):
    music_clips = {}  # maps mediaID to XML MusicClip
    external_clips = {}  # maps mediaID to XML ExternalClip
    packages = []  # list of XML package Association
    doc_path = None  # XML documentPath
    
    def __init__(self, fn):
        super(MediaPool, self).__init__(fn)
        for child in self.tree:
            if child.tag == 'Attributes':
                id = child.get("x:id")
                if id == 'rootFolder':
                    self.parse_root(child)
                elif id == 'packageInfos':
                    for a in child:
                        self.packages.append(a)
                elif id == 'documentPath':
                    self.doc_path = child

    def parse_root(self, root):
        for folder in root:
            if folder.get("name") == "Music":
                for mc in folder:
                    if mc.tag == 'MusicClip':
                        self.music_clips[mc.get("mediaID")] = mc
            if folder.get("name") == "Sound":
                for ec in folder:
                    if ec.tag == 'ExternalClip':
                        self.external_clips[ec.get("mediaID")] = ec

    def get_mc_file(self, mediaID):
        mc = self.music_clips[mediaID]
        for child in mc:
            if child.tag == 'Url':
                return child.get("url").split("media://")[1]

    def get_ec_file(self, mediaID):
        ec = self.external_clips[mediaID]
        for child in ec:
            if child.tag == 'Url':
                return child.get("url").split("package://")[1]

    def get_doc_path(self):
        dp = self.doc_path.get("url")
        return dp.split("file://")[1]

    def add_music_clip(self, clip):
        self.add_sibling(self.music_clips, clip)
        self.music_clips[clip.get("mediaID")] = clip

    def add_external_clip(self, clip):
        self.add_sibling(self.external_clips, clip)
        self.external_clips[clip.get("mediaID")] = clip

    def add_package(self, package):
        p = self.packages[0].getparent()
        p.append(package)
        self.packages.append(package)

    def set_doc_path(self, doc_path):
        p = self.doc_path.getparent()
        p.replace(self.doc_path, doc_path)
        self.doc_path = doc_path

if __name__ == "__main__":
    mp = MediaPool(sys.argv[1])
    print mp.get_mc_file(mp.music_clips.keys()[0])
    print mp.get_doc_path()
