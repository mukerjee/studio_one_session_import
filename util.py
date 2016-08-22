#!/usr/bin/python

import os
import shutil
from lxml import etree


def replace_tempo_map(src, dst):
    dst.song.set_tempo_map(src.song.tempo_map)


def replace_time_sig_map(src, dst):
    dst.song.set_time_sig_map(src.song.time_sig_map)


def replace_marker_track(src, dst):
    dst.song.set_marker_track(src.song.marker_track)


def replace_arranger_track(src, dst):
    dst.song.set_arranger_track(src.song.arranger_track)


def import_melodyne_data(src, dst):
    if os.path.exists(src.prefix + '/ARA/'):
        shutil.copytree(src.prefix + '/ARA/', dst.prefix + '/ARA/')


def import_track(src, dst, track_name, options):
    uid = src.song.track_names[track_name]
    track = src.song.tracks[uid]
    type = src.song.get_track_type(uid)

    ae = src.song.get_automation(uid)
    for a in ae:
        if not os.path.exists(dst.prefix + '/Envelopes/' + track_name):
            os.makedirs(dst.prefix + '/Envelopes/' + track_name)
        shutil.copyfile(src.prefix + a, dst.prefix + a)
        if 'automation' not in options:
            t = etree.fromstring(open(dst.prefix + a).read())
            for c in t:
                t.remove(c)
            fp = open(dst.prefix + a, 'w')
            fp.write(etree.tostring(t))
            fp.close()
        


    if 'clips' in options:
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
    else:
        clip_list = track.xpath("List[@x:id='Layers'] | List[@x:id='Events']",
                                namespaces={'x': 'x'})
        if len(clip_list):
            track.remove(clip_list[0])

            
    if 'event FX' in options:
        for clip_effect in src.song.get_clip_effect_ids(uid):
            dst.mediapool.add_clip(src.mediapool.clips[clip_effect])
            for cef in src.mediapool.get_clip_effect_files(clip_effect):
                clip_name = cef.split("/Presets/")[1].split("/")[0]
                if not os.path.exists(dst.prefix + '/Presets/' + clip_name):
                    os.makedirs(dst.prefix + '/Presets/' + clip_name)
                shutil.copyfile(src.prefix + cef, dst.prefix + cef)
    else:
        fx = track.xpath("*/*/*/AudioEvent/Attributes[@x:id='effects'] |" +
                         "*/AudioEvent/Attributes[@x:id='effects']",
                         namespaces={'x': 'x'})
        for f in fx:
            f.getparent().remove(f)


    dst.song.add_track(track)

    ch_id = src.song.get_channel_id(uid)
    am_id = None

    if type == "Music":
        dst.musictrackdevice.add_channel(
            src.musictrackdevice.channels[ch_id])
        asf_id = src.musictrackdevice.get_destination(ch_id)

        if asf_id and 'instrument' in options:
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

            ch = src.audiomixer.channels[t]

            if 'sends' in options:
                unexplored += src.audiomixer.get_sends(t)
            else:
                s = ch.xpath("Attributes[@x:id='Sends']",
                             namespaces={'x': 'x'})
                if len(s):
                    ch.remove(s[0])

            if 'buses / destinations' in options:
                d = src.audiomixer.get_destination(t)
                d_t = src.audiomixer.get_type(d)
                if d_t != 'AudioOutputChannel' and d_t != 'None':
                    unexplored.append(d)

            if 'vca' not in options:
                v = ch.xpath("Attributes[@x:id='VCATarget']",
                             namespaces={'x': 'x'})
                if len(v):
                    ch.remove(v[0])
                
            dst.audiomixer.add_channel(ch)
            tracks.append(t)

        for id in tracks:
            vca = src.audiomixer.get_vca(id)
            if vca and 'vca' in options:
                dst.audiomixer.add_channel(src.audiomixer.channels[vca])
                tracks.append(vca)
                    
            
        for id in tracks:
            if 'inserts' in options:
                inserts = src.audiomixer.get_inserts(id)
                name = src.audiomixer.get_name(id)
                for insert in inserts:
                    if not os.path.exists(dst.prefix + '/Presets/Channels/' + name):
                        os.makedirs(dst.prefix + '/Presets/Channels/' + name)
                    shutil.copyfile(src.prefix + insert, dst.prefix + insert)
            else:
                ch = dst.audiomixer.channels[id]
                i = ch.xpath("Attributes[@x:id='Inserts']/Attributes[@name]",
                             namespaces={'x': 'x'})
                if len(i):
                    ch.remove(i[0].getparent())

            dst.mixerconsole.add_channel_setting(
                src.mixerconsole.channel_settings[id])
            dst.mixerconsole.add_channel_to_banks(
                src.mixerconsole.channels_in_bank[id])
