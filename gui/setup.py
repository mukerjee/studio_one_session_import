"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['S1ImportGUI.py']
DATA_FILES = ['S1ImportGUI.xib', '../song_model.py', '../util.py', '../parsers/audio_mixer.py', '../parsers/audio_synth_folder.py', '../parsers/media_pool.py', '../parsers/mixer_console.py', '../parsers/music_track_device.py', '../parsers/song.py', '../parsers/song_parser.py']
OPTIONS = {
    "includes": ['lxml.etree'],
    "packages": ['lxml'],
    "frameworks": ['/usr/lib/libxml2.2.dylib']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
