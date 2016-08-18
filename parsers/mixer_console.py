#!/usr/bin/python

import sys
from lxml import etree
from song_parser import Parser


class MixerConsole(Parser):
    def __init__(self, fn):
        super(MixerConsole, self).__init__(fn)

        self.channel_settings = {}  # maps (correct) UIDs to XML Section
        self.channel_banks = {}  # maps bank id to XML ChannelShowHidPresets
        self.channels_in_bank = {}  # maps UIDs to XML UID
        self.max = 0
    
        for child in self.tree:
            id = child.get("x:id")
            if id == "channelSettings":
                self.parse_channel_settings(child)
            elif id == "layoutSettings":
                pass
            elif id == "channelBanks":
                self.parse_channel_banks(child)
            elif id == "HardwareControls":
                pass

    def parse_channel_settings(self, root):
        for child in root:
            uid = child.get("path")
            uid = '{%s-%s-%s-%s-%s}' % (uid[:8], uid[8:12],
                                        uid[12:16], uid[16:20], uid[20:])
            for a in child:
                if a.tag == "Attributes":
                    self.max = max(self.max, int(a.get("order")))
            self.channel_settings[uid] = child

    def parse_channel_banks(self, root):
        for child in root:
            id = child.get("x:id")
            for a in child:
                if a.get("x:id") == "visible":
                    for b in a:
                        self.channels_in_bank[b.get("uid")] = b
            self.channel_banks[id] = child
            
    def get_visible_in_bank(self, bank):
        visible = []
        for child in self.channel_banks[bank]:
            if child.get("x:id") == "visible":
                for v in child:
                    visible.append(v.get("uid"))
        return visible

    def add_channel_setting(self, channel_setting):
        self.add_sibling(self.channel_settings, channel_setting)
        uid = channel_setting.get("path")
        uid = '{%s-%s-%s-%s-%s}' % (uid[:8], uid[8:12],
                                    uid[12:16], uid[16:20], uid[20:])
        for a in channel_setting:
            if a.tag == "Attributes":
                a.set("order", str(int(a.get("order")) + self.max))
        self.channel_settings[uid] = channel_setting

    def add_channel_to_banks(self, channel):
        for id in self.channel_banks:
            v = None
            for c in self.channel_banks[id]:
                if c.get("x:id") == "visible":
                    v = c
            if v is None:
                parser = etree.XMLParser(recover=True)
                v = etree.fromstring('<List x:id="visible"/>', parser)
                self.channel_banks[id].append(v)
            v.append(channel)
            
if __name__ == "__main__":
    mc = MixerConsole(sys.argv[1])
    for c in mc.get_visible_in_bank("ScreenBank"):
        print c in mc.channel_settings
