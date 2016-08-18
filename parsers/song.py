#!/usr/bin/python

import sys
from collections import OrderedDict
from song_parser import Parser


class Song(Parser):
    def __init__(self, fn):
        super(Song, self).__init__(fn)

        self.tempo_map = None  # XML TempoMap
        self.time_sig_map = None  # XML TimeSignatureMap
        self.time_zone_map = None  # XML TimeZoneMap
        self.tracks = OrderedDict()  # maps trackID to XML MediaTrack
        self.parent_track = None  # XML <List x:id="Tracks">
        self.track_names = OrderedDict()  # maps track names to trackID
        self.marker_track = None  # XML MarkerTrack
        self.arranger_track = None  # XML ArrangerTrack

        for child in self.tree:
            if child.tag == "Attributes":
                id = child.get("x:id")
                if id == "Root":
                    self.parse_root(child)
        for track in self.tracks:
            self.track_names[self.get_track_name(track)] = track

    def parse_root(self, root):
        for child in root:
            id = child.get("x:id")
            if id == "timeContext":
                self.parse_time(child)
            elif id == "Tracks":
                self.parse_tracks(child)
            
    def parse_time(self, root):
        for child in root:
            if child.tag == "TempoMap":
                self.tempo_map = child
            elif child.tag == "TimeSignatureMap":
                self.time_sig_map = child
            elif child.tag == "TimeZoneMap":
                self.time_zone_map = child

    def parse_tracks(self, root):
        self.parent_track = root
        for child in root:
            if child.tag == "MediaTrack":
                self.tracks[child.get("trackID")] = child
            if child.tag == "MarkerTrack":
                self.marker_track = child
            if child.tag == "ArrangerTrack":
                self.arranger_track = child

    def parse_media_track_list(self, root):
        clip_ids = []
        for child in root:
            if child.tag == "List":
                if child.get("x:id") == "Layers":
                    for layer in child:
                        if layer.tag == "Attributes" and layer.get("layerName"):
                            clip_ids += self.parse_media_track_list(layer)
                if child.get("x:id") == "Events":
                    for mp in child:
                        if mp.tag == "MusicPart":
                            clip_ids.append(mp.get("clipID"))
        return clip_ids

    def get_track_name(self, trackID):
        return self.tracks[trackID].get("name")

    def get_channel_id(self, trackID):
        for child in self.tracks[trackID]:
            if child.tag == 'UID' and child.get("x:id") == "channelID":
                return child.get("uid")

    def get_music_part_clip_ids(self, trackID):
        if self.tracks[trackID].get("mediaType") != "Music":
            return []
        return self.parse_media_track_list(self.tracks[trackID])

    def set_tempo_map(self, tm):
        self.swap(self.tempo_map, tm)
        self.tempo_map = tm

    def set_time_sig_map(self, tsm):
        self.swap(self.time_sig_map, tsm)
        self.time_sig_map = tsm

    def set_time_zone_map(self, tzm):
        self.swap(self.time_zone_map, tzm)
        self.time_zone_map = tzm

    def set_marker_track(self, mt):
        self.swap(self.marker_track, mt)
        self.marker_track = mt

    def set_arranger_track(self, at):
        self.swap(self.arranger_track, at)
        self.arranger_track = at

    def add_track(self, track):
        self.parent_track.append(track)
        tid = track.get("trackID")
        name = track.get("name")
        self.tracks[tid] = track
        self.track_names[name] = tid


if __name__ == "__main__":
    s = Song(sys.argv[1])
    name = s.track_names.keys()[0]
    print name
    tid = s.track_names[name]
    print s.get_channel_id(tid)
    print s.get_music_part_clip_ids(tid)
