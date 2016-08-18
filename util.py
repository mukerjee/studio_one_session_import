#!/usr/bin/python

import os
import shutil


def import_music_track(src, dst, track_name):
    uid = src.song.track_names[track_name]
    track = src.song.tracks[uid]
    dst.song.add_track(track)

    clips = src.song.get_music_part_clip_ids(uid)
    for clip in clips:
        dst.mediapool.add_music_clip(src.mediapool.music_clips[clip])
        if not os.path.exists(dst.prefix + '/Performances'):
            os.makedirs(dst.prefix + '/Performances')
        if not os.path.exists(dst.prefix + '/Performances/' + track_name):
            os.makedirs(dst.prefix + '/Performances/' + track_name)
        shutil.copyfile(src.prefix + src.mediapool.get_mc_file(clip),
                        dst.prefix + src.mediapool.get_mc_file(clip))

    ch_id = src.song.get_channel_id(uid)
    dst.musictrackdevice.add_channel(
        src.musictrackdevice.channels[ch_id])
    asf_id = src.musictrackdevice.get_destination(ch_id)

    dst.audiosynthfolder.add_synth(src.audiosynthfolder.synths[asf_id])
    preset = src.audiosynthfolder.get_synth_preset(asf_id)
    if not os.path.exists(dst.prefix + '/Presets'):
        os.makedirs(dst.prefix + '/Presets')
    if not os.path.exists(dst.prefix + '/Presets/Synths'):
        os.makedirs(dst.prefix + '/Presets/Synths')
    shutil.copyfile(src.prefix + preset, dst.prefix + preset)

    am_id = src.musictrackdevice.get_instrument_out(ch_id)
    dst.audiomixer.add_synth(src.audiomixer.synths[am_id])

    dst.mixerconsole.add_channel_setting(
        src.mixerconsole.channel_settings[am_id])
    dst.mixerconsole.add_channel_to_banks(
        src.mixerconsole.channels_in_bank[am_id])
