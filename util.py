#!/usr/bin/python

import os
import shutil

KEEP_CLIPS = True


def replace_tempo_map(src, dst):
    dst.song.set_tempo_map(src.song.tempo_map)


def replace_time_sig_map(src, dst):
    dst.song.set_time_sig_map(src.song.time_sig_map)


def replace_marker_track(src, dst):
    dst.song.set_marker_track(src.song.marker_track)


def replace_arranger_track(src, dst):
    dst.song.set_arranger_track(src.song.arranger_track)


def import_track(src, dst, track_name):
    uid = src.song.track_names[track_name]
    track = src.song.tracks[uid]
    type = src.song.get_track_type(uid)

    if KEEP_CLIPS:
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
                if os.path.dirname(os.path.abspath(src.fn)) + '/Media' == \
                   os.path.dirname(src.mediapool.get_file(clip)):
                    # internal clip
                    src_base = os.path.dirname(src.fn)
                    dst_base = os.path.dirname(dst.fn)
                    if src_base == dst_base:
                        break
                    if not os.path.exists(dst_base + '/Media'):
                        os.makedirs(dst_base + '/Media')
                    loc = '/Media/' + \
                          src.mediapool.get_file(clip).split("/Media/")[1]
                    shutil.copyfile(src_base + loc, dst_base + loc)
                else:
                    # TODO: External files?
                    pass

        ae = src.song.get_automation(uid)
        for a in ae:
            if not os.path.exists(dst.prefix + '/Envelopes/' + track_name):
                os.makedirs(dst.prefix + '/Envelopes/' + track_name)
            shutil.copyfile(src.prefix + a, dst.prefix + a)
    else:
        clip_list = track.xpath("List[@x:id='Layers'] | List[@x:id='Events']",
                                namespaces={'x': 'x'})
        if len(clip_list):
            track.remove(clip_list[0])

        dst.song.add_track(track)

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
        tracks = []
        unexplored = [am_id]

        while len(unexplored):
            t = unexplored.pop(0)

            unexplored += src.audiomixer.get_sends(t)

            d = src.audiomixer.get_destination(t)
            d_t = src.audiomixer.get_type(d)
            if d_t != 'AudioOutputChannel' and d_t != 'None':
                unexplored.append(d)

            dst.audiomixer.add_channel(src.audiomixer.channels[t])
            tracks.append(t)

        for id in tracks:
            vca = src.audiomixer.get_vca(id)
            if vca:
                dst.audiomixer.add_channel(src.audiomixer.channels[vca])
                tracks.append(vca)
            
        for id in tracks:
            inserts = src.audiomixer.get_inserts(id)
            name = src.audiomixer.get_name(id)
            for insert in inserts:
                if not os.path.exists(dst.prefix + '/Presets/Channels/' + name):
                    os.makedirs(dst.prefix + '/Presets/Channels/' + name)
                shutil.copyfile(src.prefix + insert, dst.prefix + insert)

            dst.mixerconsole.add_channel_setting(
                src.mixerconsole.channel_settings[id])
            dst.mixerconsole.add_channel_to_banks(
                src.mixerconsole.channels_in_bank[id])
