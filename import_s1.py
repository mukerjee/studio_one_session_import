#!/usr/bin/python

import sys
from song_model import SongModel
from util import replace_tempo_map, replace_time_sig_map, \
    replace_marker_track, import_track

src_song = SongModel(sys.argv[1])
dst_song = SongModel(sys.argv[2])

replace_tempo_map(src_song, dst_song)
replace_time_sig_map(src_song, dst_song)
replace_marker_track(src_song, dst_song)

tracks = src_song.song.track_names.keys()
print tracks
for track in tracks:
    import_track(src_song, dst_song, track)

    
dst_song.write()

src_song.clean()
dst_song.clean()
