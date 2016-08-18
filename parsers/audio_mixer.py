#!/usr/bin/python

import sys
from lxml import etree
from song_parser import Parser


class AudioMixer(Parser):
    def __init__(self, fn):
        super(AudioMixer, self).__init__(fn)

        self.outputs = {}  # maps channel uid to XML AudioOutputChannel
        self.inputs = {}  # maps channel uid to XML AudioInputChannel
        self.synths = {}  # maps channel uid to XML AudioSynthChannel
    
        for child in self.tree:
            if child.tag == "Attributes":
                id = child.get("x:id")
                if id == "channels":
                    self.parse_root(child)

    def parse_root(self, root):
        for child in root:
            if child.tag == "ChannelGroup":
                name = child.get("name")
                if name == "AudioOutput":
                    self.parse_outputs(child)
                elif name == "AudioInput":
                    self.parse_inputs(child)
                elif name == "AudioSynth":
                    self.parse_synths(child)

    def parse_outputs(self, root):
        for child in root:
            if child.tag == "AudioOutputChannel":
                for t in child:
                    id = t.get("x:id")
                    if id == "uniqueID":
                        uid = t.get("uid")
                self.outputs[uid] = child

    def parse_inputs(self, root):
        for child in root:
            if child.tag == "AudioInputChannel":
                for t in child:
                    id = t.get("x:id")
                    if id == "uniqueID":
                        uid = t.get("uid")
                self.inputs[uid] = child

    def parse_synths(self, root):
        for child in root:
            if child.tag == "AudioSynthChannel":
                for t in child:
                    id = t.get("x:id")
                    if id == "uniqueID":
                        uid = t.get("uid")
                self.synths[uid] = child

    def parse_inserts(self, root):
        inserts = []
        for child in root:
            for a in child:
                if a.get("x:id") == "presetPath":
                    inserts.append("/" + a.get("text"))
        return inserts

    def get_synth_name(self, trackID):
        return self.synths[trackID].get("label")

    def get_synth_destination(self, trackID):
        for t in self.synths[trackID]:
            id = t.get("x:id")
            if id == "destination":
                return t.get("objectID").split("/")[0]

    def get_synth_inserts(self, trackID):
        for t in self.synths[trackID]:
            id = t.get("x:id")
            if id == "Inserts":
                return self.parse_inserts(t)

    def add_output(self, output):
        self.add_sibling(self.outputs, output)
        for t in output:
            if t.get("x:id") == "uniqueID":
                uid = t.get("uid")
        self.outputs[uid] = output

    def add_input(self, input):
        self.add_sibling(self.inputs, input)
        for t in input:
            if t.get("x:id") == "uniqueID":
                uid = t.get("uid")
        self.inputs[uid] = input

    def add_synth(self, synth):
        if len(self.synths):
            self.add_sibling(self.synths, synth)
        else:
            for child in self.tree:
                if child.get("x:id") == "channels":
                    cg = None
                    for a in child:
                        if a.get("name") == "AudioSynth":
                            cg = a
                    if not cg:
                        cg = etree.Element("ChannelGroup")
                        cg.set("name", "AudioSynth")
                        cg.set("flags", "1")
                        child.append(cg)
                    cg.append(synth)
        for t in synth:
            if t.get("x:id") == "uniqueID":
                uid = t.get("uid")
        self.synths[uid] = synth

if __name__ == "__main__":
    am = AudioMixer(sys.argv[1])
    tid = am.synths.keys()[4]
    print am.get_synth_name(tid)
    print am.get_synth_destination(tid)
    print am.get_synth_inserts(tid)
