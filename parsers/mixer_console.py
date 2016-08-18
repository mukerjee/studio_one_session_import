#!/usr/bin/python

import sys
from song_parser import Parser


class MixerConsole(Parser):
    channel_settings = {}  # maps (correct) UIDs to XML Section
    channel_banks = {}  # maps bank id to XML ChannelShowHidPresets
    
    def __init__(self, fn):
        super(MixerConsole, self).__init__(fn)
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
            self.channel_settings[uid] = child

    def parse_channel_banks(self, root):
        for child in root:
            id = child.get("x:id")
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
        self.channel_settings[uid] = channel_setting

    def add_channel_to_banks(self, channel):
        for id in self.channel_banks:
            for c in self.channel_banks[id]:
                if c.get("x:id") == "visible":
                    c.append(channel)
            
if __name__ == "__main__":
    mc = MixerConsole(sys.argv[1])
    for c in mc.get_visible_in_bank("ScreenBank"):
        print c in mc.channel_settings
