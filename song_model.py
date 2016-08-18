#!/usr/bin/python

import sys
sys.path.append("./parsers/")

import os
import zipfile
import shutil

from audio_mixer import AudioMixer
from audio_synth_folder import AudioSynthFolder
from media_pool import MediaPool
from mixer_console import MixerConsole
from music_track_device import MusicTrackDevice
from song import Song

DONT_OVERWRITE = True

class SongModel(object):
    fn = None
    prefix = None
    song = None
    musictrackdevice = None
    audiosynthfolder = None
    mediapool = None
    mixerconsole = None
    audiomixer = None
    clean = True
    
    def __init__(self, fn):
        self.fn = fn
        self.prefix = os.path.splitext(fn)[0]
        self.extract()
        if DONT_OVERWRITE:
            self.fn = self.prefix + '-new.song'
        self.song = Song(self.prefix + '/Song/song.xml')
        self.musictrackdevice = MusicTrackDevice(
            self.prefix + '/Devices/musictrackdevice.xml')
        self.audiosynthfolder = AudioSynthFolder(
            self.prefix + '/Devices/audiosynthfolder.xml')
        self.mediapool = MediaPool(self.prefix + '/Song/mediapool.xml')
        self.mixerconsole = MixerConsole(
            self.prefix + '/Devices/mixerconsole.xml')
        self.audiomixer = AudioMixer(self.prefix + '/Devices/audiomixer.xml')

    def extract(self):
        f = zipfile.ZipFile(self.fn, 'r')
        f.extractall(self.prefix)
        f.close()
        self.clean = False

    def compress(self):
        f = zipfile.ZipFile(self.fn, 'w', zipfile.ZIP_DEFLATED)
        os.chdir(self.prefix)
        for root, dirs, files in os.walk('./'):
            for file in files:
                f.write(os.path.join(root, file))
        f.close()
        os.chdir('../')

    def delete_temp(self):
        shutil.rmtree(self.prefix)
        self.clean = True

    def clean(self):
        if not self.clean:
            self.delete_temp()
            self.clean = True

    def write(self):
        self.song.write()
        self.musictrackdevice.write()
        self.audiosynthfolder.write()
        self.mediapool.write()
        self.mixerconsole.write()
        self.audiomixer.write()
        self.compress()
        self.delete_temp()

