#!/usr/bin/python

import sys
from song_model import SongModel
from util import import_music_track

src_song = SongModel(sys.argv[1])
dst_song = SongModel(sys.argv[2])

dst_song.song.set_tempo_map(src_song.song.tempo_map)
dst_song.song.set_time_sig_map(src_song.song.time_sig_map)
dst_song.song.set_marker_track(src_song.song.marker_track)

tracks = src_song.song.track_names.keys()
# bass = tracks[-1]
# import_music_track(src_song, dst_song, bass)
for track in tracks:
    import_music_track(src_song, dst_song, track)

    
dst_song.write()

src_song.clean()
dst_song.clean()
