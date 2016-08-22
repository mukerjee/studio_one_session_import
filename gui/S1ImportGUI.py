import Cocoa
import AppKit
from PyObjCTools import AppHelper
from Foundation import NSObject
import os

import sys
sys.path.append('./')
sys.path.append('/Library/Python/2.7/site-packages/' +
                'lxml-3.3.1-py2.7-macosx-10.9-intel.egg')
from song_model import SongModel
from util import replace_tempo_map, replace_time_sig_map, \
    replace_marker_track, replace_arranger_track, import_track


TRACK_OPTIONS = (
    'clips',
    'inserts',
    'automation',
    'sends',
    'busses / destinations',
    'event FX',
    'melodyne',
)


class S1ImportGUIController(Cocoa.NSWindowController):
    srcSongLabel = Cocoa.objc.IBOutlet()
    dstSongLabel = Cocoa.objc.IBOutlet()
    trackOutlineView = Cocoa.objc.IBOutlet()
    tempomapCheckBox = Cocoa.objc.IBOutlet()
    timesigmapCheckBox = Cocoa.objc.IBOutlet()
    markertrackCheckBox = Cocoa.objc.IBOutlet()
    arrangertrackCheckBox = Cocoa.objc.IBOutlet()

    def init(self):
        self.src_song = None
        self.dst_song = None
        self.srcSongLabel.setStringValue_("")
        self.dstSongLabel.setStringValue_("")
        self.pythonItems = {}

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
        print 'did load'
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
            self.trackOutlineView.reloadData()

    @Cocoa.objc.IBAction
    def opendst_(self, sender):
        s = self.open_box()
        if s:
            self.dst_song = SongModel(s)
            self.dstSongLabel.setStringValue_(
                os.path.basename(self.dst_song.fn).split('-new.song')[0]
                + '.song')

    @Cocoa.objc.IBAction
    def import_(self, sender):
        if self.dst_song:
            if self.tempomapCheckBox.state():
                replace_tempo_map(self.src_song, self.dst_song)
            if self.timesigmapCheckBox.state():
                replace_time_sig_map(self.src_song, self.dst_song)
            if self.markertrackCheckBox.state():
                replace_marker_track(self.src_song, self.dst_song)
            if self.arrangertrackCheckBox.state():
                replace_arranger_track(self.src_song, self.dst_song)
            # TODO:
            # for track in self.trackTextBox.stringValue().split('\n'):
            #     import_track(self.src_song, self.dst_song, track)
            self.dst_song.write()
        self.quit_(None)

    @Cocoa.objc.IBAction
    def quit_(self, sender):
        if self.src_song:
            self.src_song.clean()
        if self.dst_song:
            self.dst_song.clean()
        AppKit.NSApp().terminate_(self)

    # NSTableViewDataSource
    # TODO: I don't think this is called ever
    # def numberOfRowsInTableView_(self, tableView):
    #     print 'num rows'
    #     print 'omgomgomgomg'
    #     if not hasattr(self, 'src_song') or self.src_song is None:
    #         return 0
    #     else:
    #         return len(self.src_song.song.track_names.keys())

    # NSOutlineViewDataSource
    def outlineView_numberOfChildrenOfItem_(self, outlineView, item):
        print 'num children of %s' % item
        if item is None:
            if not hasattr(self, 'src_song') or self.src_song is None:
                return 0
            else:
                return len(self.src_song.song.track_names.keys())
        elif item.name in TRACK_OPTIONS:
            return 0
        else:
            return len(TRACK_OPTIONS)
    
    def outlineView_isItemExpandable_(self, outlineView, item):
        if item:
            return False if item.name in TRACK_OPTIONS else True
        else:
            return True

    def outlineView_child_ofItem_(self, outlineView, index, item):
        if item is None:
            return self.getPythonItem(self.src_song.song.track_names.keys()[index])
        else:
            return self.getPythonItem(TRACK_OPTIONS[index])

    def getPythonItem(self, item):
        if item in self.pythonItems:
            return self.pythonItems[item]
        else:
            i = PythonItem(item)
            self.pythonItems[item] = i
            return i

    # TODO: not sure what the point of this call is
    def outlineView_objectValueForTableColumn_byItem_(
            self, outlineView, tableColumn, item):
        return item.name

    def outlineView_viewForTableColumn_item_(
            self, outlineView, tableColumn, item):
        # print 'view for %s' % item.name

        tcv = outlineView.makeViewWithIdentifier_owner_("MainCell", self)
        tcv.textField().setStringValue_(item.name)
        
        #NSImage* cellImage;
        #
        #if (HAS_KEY(item,@"children")) cellImage = [[NSWorkspace sharedWorkspace] iconForFileType:NSFileTypeForHFSTypeCode(kGenericFolderIcon)];
        #else cellImage = [[NSWorkspace sharedWorkspace] iconForFileType:NSFileTypeRegular];
        
        #[cellImage setSize:NSMakeSize(15.0, 15.0)];
        
        #tcv.imageView.image = cellImage;
        
        return tcv


class PythonItem(NSObject):

    """Wrapper class for items to be displayed in the outline view."""

    def __new__(cls, *args, **kwargs):
        # "Pythonic" constructor
        return cls.alloc().init()

    def __init__(self, name):
        self.name = name

if __name__ == "__main__":
    app = Cocoa.NSApplication.sharedApplication()
    
    # Initiate the contrller with a XIB
    viewController = \
        S1ImportGUIController.alloc().initWithWindowNibName_("S1ImportGUIMenu")

    # Show the window
    viewController.showWindow_(viewController)

    # Bring app to top
    Cocoa.NSApp.activateIgnoringOtherApps_(True)
    
    AppHelper.runEventLoop()
