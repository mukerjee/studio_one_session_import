#!/usr/bin/python

import sys
from lxml import etree
from song_parser import Parser


class MusicTrackDevice(Parser):
    def __init__(self, fn):
        super(MusicTrackDevice, self).__init__(fn)

        self.channels = {}  # maps UID to XML MusicTrackChannel

        for child in self.tree:
            id = child.get("x:id")
            if id == "channels":
                self.parse_channels(child)

    def parse_channels(self, root):
        for child in root:
            name = child.get("name")
            if name == "MusicTrack":
                for channel in child:
                    for a in channel:
                        if a.get("x:id") == "uniqueID":
                            uid = a.get("uid")
                    self.channels[uid] = channel

    def get_instrument_out(self, uid):
        for child in self.channels[uid]:
            if child.get("x:id") == "instrumentOut":
                return child.get("objectID").split('/')[0]

    def get_destination(self, uid):
        for child in self.channels[uid]:
            if child.get("x:id") == "destination":
                return child.get("objectID").split('/')[0]

    def add_channel(self, channel):
        if len(self.channels):
            self.add_sibling(self.channels, channel)
        else:
            for child in self.tree:
                if child.get("x:id") == "channels":
                    cg = None
                    for a in child:
                        if a.get("name" == "MusicTrack"):
                            cg = a
                    if not cg:
                        cg = etree.Element("ChannelGroup")
                        cg.set("name", "MusicTrack")
                        cg.set("flags", "1")
                        child.append(cg)
                    cg.append(channel)
        for a in channel:
            if a.get("x:id") == "uniqueID":
                uid = a.get("uid")
        self.channels[uid] = channel

            
if __name__ == "__main__":
    mtd = MusicTrackDevice(sys.argv[1])
    print mtd.get_instrument_out(mtd.channels.keys()[0])
    print mtd.get_destination(mtd.channels.keys()[0])
