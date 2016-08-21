import Cocoa
import AppKit
from PyObjCTools import AppHelper
from Foundation import NSObject
import os

import sys
sys.path.append('./')
sys.path.append('/Library/Python/2.7/site-packages/lxml-3.3.1-py2.7-macosx-10.9-intel.egg')
from song_model import SongModel
from util import replace_tempo_map, replace_time_sig_map, \
    replace_marker_track, replace_arranger_track, import_track


class S1ImportGUIController(Cocoa.NSWindowController):
    srcSongLabel = Cocoa.objc.IBOutlet()
    dstSongLabel = Cocoa.objc.IBOutlet()
    trackTextBox = Cocoa.objc.IBOutlet()

    def init(self):
        self.src_song = None
        self.dst_song = None
        self.tempomap_enabled = True
        self.timesigmap_enabled = True
        self.markertrack_enabled = True
        self.arrangertrack_enabled = True
        self.srcSongLabel.setStringValue_("")
        self.dstSongLabel.setStringValue_("")
        self.trackTextBox.setStringValue_("")

    def open_box(self):
        op = Cocoa.NSOpenPanel.openPanel()
        op.setCanChooseDirectories_(False)
        op.setCanChooseFiles_(True)
        op.setResolvesAliases_(True)
        op.setAllowsMultipleSelection_(False)
        if op.runModal() == Cocoa.NSOKButton:
            return op.filename()
        else:
            return ""

    def windowDidLoad(self):
        Cocoa.NSWindowController.windowDidLoad(self)
        if not hasattr(self, 'src_song'):
            self.init()

    @Cocoa.objc.IBAction
    def opensrc_(self, sender):
        s = self.open_box()
        if s:
            self.src_song = SongModel(s)
            self.srcSongLabel.setStringValue_(
                os.path.basename(self.src_song.fn).split('-new.song')[0]
                + '.song')
            self.trackTextBox.setStringValue_(
                '\n'.join(self.src_song.song.track_names.keys()))

    @Cocoa.objc.IBAction
    def opendst_(self, sender):
        s = self.open_box()
        if s:
            self.dst_song = SongModel(s)
            self.dstSongLabel.setStringValue_(
                os.path.basename(self.dst_song.fn).split('-new.song')[0]
                + '.song')

    @Cocoa.objc.IBAction
    def tempomap_(self, sender):
        self.tempomap_enabled = sender.state()

    @Cocoa.objc.IBAction
    def timesigmap_(self, sender):
        self.timesigmap_enabled = sender.state()

    @Cocoa.objc.IBAction
    def markertrack_(self, sender):
        self.markertrack_enabled = sender.state()

    @Cocoa.objc.IBAction
    def arrangertrack_(self, sender):
        self.arrangertrack_enabled = sender.state()
    
    @Cocoa.objc.IBAction
    def import_(self, sender):
        if self.dst_song:
            if self.tempomap_enabled:
                replace_tempo_map(self.src_song, self.dst_song)
            if self.timesigmap_enabled:
                replace_time_sig_map(self.src_song, self.dst_song)
            if self.markertrack_enabled:
                replace_marker_track(self.src_song, self.dst_song)
            if self.arrangertrack_enabled:
                replace_arranger_track(self.src_song, self.dst_song)
            for track in self.trackTextBox.stringValue().split('\n'):
                import_track(self.src_song, self.dst_song, track)
            self.dst_song.write()
        self.quit_(None)

    @Cocoa.objc.IBAction
    def quit_(self, sender):
        if self.src_song:
            self.src_song.clean()
        if self.dst_song:
            self.dst_song.clean()
        AppKit.NSApp().terminate_(self)


if __name__ == "__main__":
    app = Cocoa.NSApplication.sharedApplication()
    
    # Initiate the contrller with a XIB
    viewController = \
        S1ImportGUIController.alloc().initWithWindowNibName_("S1ImportGUI")

    # Show the window
    viewController.showWindow_(viewController)

    # Bring app to top
    Cocoa.NSApp.activateIgnoringOtherApps_(True)
    
    AppHelper.runEventLoop()
