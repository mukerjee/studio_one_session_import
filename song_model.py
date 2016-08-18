#!/usr/bin/python

import sys
sys.path.append("./parsers/")

from audio_mixer import AudioMixer
from audio_synth_folder import AudioSynthFolder
from media_pool import MediaPool
from mixer_console import MixerConsole
from music_track_device import MusicTrackDevice
from song import Song


class SongModel(object):
    def __init__(self, prefix):
        self.song = Song(prefix + '/Song/song.xml')
        self.musictrackdevice = MusicTrackDevice(prefix + '/Devices/musictrackdevice.xml')
        self.audiosynthfolder = AudioSynthFolder(prefix + '/Devices/audiosynthfolder.xml')
        self.mediapool = MediaPool(prefix + '/Song/mediapool.xml')
        self.mixerconsole = MixerConsole(prefix + '/Devices/mixerconsole.xml')
        self.audiomixer = AudioMixer(prefix + '/Devices/audiomixer.xml')
