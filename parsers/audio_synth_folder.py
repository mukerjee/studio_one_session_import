#!/usr/bin/python

import sys
from parser import Parser


class AudioSynthFolder(Parser):
    synths = {}  # maps synth deviceData UID to XML Synth Attributes
    
    def __init__(self, fn):
        super(AudioSynthFolder, self).__init__(fn)
        for child in self.tree:
            if child.get("x:id") != "Presets":
                self.parse_synth(child)

    def parse_synth(self, root):
        for child in root:
            id = child.get("x:id")
            if id == "deviceData":
                uid = child.get("uid")
        self.synths[uid] = root

    def get_name(self, uid):
        return self.synths[uid].get("name")

    def get_synth_name(self, uid):
        for child in self.synths[uid]:
            id = child.get("x:id")
            if id == "deviceData":
                return child.get("name")

    def get_synth_preset(self, uid):
        for child in self.synths[uid]:
            id = child.get("x:id")
            if id == "presetPath":
                return "/" + child.get("text")

if __name__ == "__main__":
    asf = AudioSynthFolder(sys.argv[1])
    print asf.synths
    tid = asf.synths.keys()[0]
    print asf.get_synth_name(tid)
    print asf.get_name(tid)
    print asf.get_synth_preset(tid)
