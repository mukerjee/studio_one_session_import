#!/usr/bin/python

import sys
from parser import Parser


class MusicTrackDevice(Parser):
    channels = {}  # maps UID to XML MusicTrackChannel

    def __init__(self, fn):
        super(MusicTrackDevice, self).__init__(fn)
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
                return child.get("objectID")

    def get_destination(self, uid):
        for child in self.channels[uid]:
            if child.get("x:id") == "destination":
                return child.get("objectID")

    def add_channel(self, channel):
        self.add_sibling(self.channels, channel)
        for a in channel:
            if a.get("x:id") == "uniqueID":
                uid = a.get("uid")
        self.channels[uid] = channel

            
if __name__ == "__main__":
    mtd = MusicTrackDevice(sys.argv[1])
    print mtd.get_instrument_out(mtd.channels.keys()[0])
    print mtd.get_destination(mtd.channels.keys()[0])
