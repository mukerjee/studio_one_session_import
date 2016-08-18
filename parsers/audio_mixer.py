#!/usr/bin/python

import sys
from parser import Parser


class AudioMixer(Parser):
    outputs = {}  # maps channel uid to XML AudioOutputChannel
    inputs = {}  # maps channel uid to XML AudioInputChannel
    synths = {}  # maps channel uid to XML AudioSynthChannel
    
    def __init__(self, fn):
        super(AudioMixer, self).__init__(fn)
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

if __name__ == "__main__":
    am = AudioMixer(sys.argv[1])
    tid = am.synths.keys()[4]
    print am.get_synth_name(tid)
    print am.get_synth_destination(tid)
    print am.get_synth_inserts(tid)
