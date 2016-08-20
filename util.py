#!/usr/bin/python

import os
import shutil


def import_track(src, dst, track_name):
    uid = src.song.track_names[track_name]
    track = src.song.tracks[uid]
    type = src.song.get_track_type(uid)
    dst.song.add_track(track)

    clips = src.song.get_clip_ids(uid)
    for clip in clips:
        dst.mediapool.add_clip(src.mediapool.clips[clip])
        if type == "Music":
            if not os.path.exists(dst.prefix + '/Performances/' + track_name):
                os.makedirs(dst.prefix + '/Performances/' + track_name)
            shutil.copyfile(src.prefix + src.mediapool.get_file(clip),
                            dst.prefix + src.mediapool.get_file(clip))
        elif type == "Audio":
            # TODO: External files
            pass

    ch_id = src.song.get_channel_id(uid)
    am_id = None

    if type == "Music":
        dst.musictrackdevice.add_channel(
            src.musictrackdevice.channels[ch_id])
        asf_id = src.musictrackdevice.get_destination(ch_id)

        if asf_id:
            dst.audiosynthfolder.add_synth(src.audiosynthfolder.synths[asf_id])
            preset = src.audiosynthfolder.get_synth_preset(asf_id)
            if not os.path.exists(dst.prefix + '/Presets/Synths'):
                os.makedirs(dst.prefix + '/Presets/Synths')
            shutil.copyfile(src.prefix + preset, dst.prefix + preset)

        am_id = src.musictrackdevice.get_instrument_out(ch_id)
    elif type == "Audio":
        am_id = ch_id

    if am_id:
        dst.audiomixer.add_channel(src.audiomixer.channels[am_id])

        inserts = src.audiomixer.get_inserts(am_id)
        for insert in inserts:
            if not os.path.exists(dst.prefix + '/Presets/Channels/' + track_name):
                os.makedirs(dst.prefix + '/Presets/Channels/' + track_name)
            shutil.copyfile(src.prefix + insert, dst.prefix + insert)

        dst.mixerconsole.add_channel_setting(
            src.mixerconsole.channel_settings[am_id])
        dst.mixerconsole.add_channel_to_banks(
            src.mixerconsole.channels_in_bank[am_id])
