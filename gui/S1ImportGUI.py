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
    replace_marker_track, replace_arranger_track, import_track, \
    import_melodyne_data


TRACK_OPTIONS = (
    'clips',
    'inserts',
    'automation',
    'sends',
    'buses / destinations',
    'event FX',
    'instrument',
    'vca',
)


class S1ImportGUIController(Cocoa.NSWindowController):
    srcSongLabel = Cocoa.objc.IBOutlet()
    dstSongLabel = Cocoa.objc.IBOutlet()
    trackOutlineView = Cocoa.objc.IBOutlet()
    tempoTimeSigMapCheckBox = Cocoa.objc.IBOutlet()
    # timesigmapCheckBox = Cocoa.objc.IBOutlet()
    markertrackCheckBox = Cocoa.objc.IBOutlet()
    arrangertrackCheckBox = Cocoa.objc.IBOutlet()
    melodyneCheckBox = Cocoa.objc.IBOutlet()

    def init(self):
        self.src_song = None
        self.dst_song = None
        self.srcSongLabel.setStringValue_("")
        self.dstSongLabel.setStringValue_("")
        self.pythonItems = {}
        self.import_set = {}
        self.checkBox_ids = {}

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
            self.trackOutlineView.reloadData()
            self.import_set = {track: list(TRACK_OPTIONS)
                               for track in self.src_song.song.track_names.keys()}

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
            if self.tempoTimeSigMapCheckBox.state():
                replace_tempo_map(self.src_song, self.dst_song)
                replace_time_sig_map(self.src_song, self.dst_song)
            # if self.timesigmapCheckBox.state():
            if self.markertrackCheckBox.state():
                replace_marker_track(self.src_song, self.dst_song)
            if self.arrangertrackCheckBox.state():
                replace_arranger_track(self.src_song, self.dst_song)
            if self.melodyneCheckBox.state():
                import_melodyne_data(self.src_song, self.dst_song)
            for track in self.src_song.song.track_names:
                if len(self.import_set[track]):
                    import_track(self.src_song, self.dst_song, track,
                                 self.import_set[track])
            self.dst_song.write()
        self.quit_(None)

    # @Cocoa.objc.IBAction
    # def quit_(self, sender):
    #     if self.src_song:
    #         self.src_song.clean()
    #     if self.dst_song:
    #         self.dst_song.clean()
    #     AppKit.NSApp().terminate_(self)

    @Cocoa.objc.IBAction
    def trackCheck_(self, sender):
        my_p, me = self.checkBox_ids[sender]
        parent_checkbox = [s for (s, (p, n)) in
                           self.checkBox_ids.items() if n == my_p]

        if my_p:
            if sender.state():
                self.import_set[my_p].append(me)
            else:
                self.import_set[my_p].remove(me)
        else:
            self.import_set[me] = list(TRACK_OPTIONS) if sender.state() \
                                  else []

        for c in [s for (s, (p, n)) in self.checkBox_ids.items() if p == me]:
            c.setState_(sender.state())

        if my_p:
            parent_checkbox[0].setState_(len(self.import_set[my_p]))

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
            name, uid = self.src_song.song.track_names.items()[index]
            return self.getPythonItem(name,
                                      self.src_song.song.get_track_type(uid),
                                      item)
        else:
            return self.getPythonItem(TRACK_OPTIONS[index], "", item)

    def getPythonItem(self, item, type, parent):
        if item in self.pythonItems:
            return self.pythonItems[(parent, item)]
        else:
            i = PythonItem(item, type, parent)
            self.pythonItems[(parent, item)] = i
            return i

    # TODO: not sure what the point of this call is
    def outlineView_objectValueForTableColumn_byItem_(
            self, outlineView, tableColumn, item):
        return item.name

    def outlineView_viewForTableColumn_item_(
            self, outlineView, tableColumn, item):
        tcv = outlineView.makeViewWithIdentifier_owner_("MainCell", self)
        n = "%s (%s)" % (item.name, item.type) if item.type else item.name
        tcv.textField().setStringValue_(n)

        p = item.get_parent_name()
        if p:
            tcv.checkBox.setState_(item.name in self.import_set[p])
        else:
            tcv.checkBox.setState_(len(self.import_set[item.name]))

        dups = [k for k, v in self.checkBox_ids.items() if v == (p, item.name)]
        for d in dups:
            del self.checkBox_ids[d]
        self.checkBox_ids[tcv.checkBox] = (p, item.name)

        return tcv
            

class TableCellViewWithCheckBox(Cocoa.NSTableCellView):
    checkBox = Cocoa.objc.IBOutlet()
    

class PythonItem(NSObject):

    """Wrapper class for items to be displayed in the outline view."""

    def __new__(cls, *args, **kwargs):
        # "Pythonic" constructor
        return cls.alloc().init()

    def __init__(self, name, type, parent):
        self.name = name
        self.type = type
        self.parent = parent

    def get_parent_name(self):
        return self.parent.name if self.parent else None

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

