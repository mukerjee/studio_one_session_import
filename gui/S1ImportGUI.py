import Cocoa
import AppKit
import PyObjCTools.Signals
from PyObjCTools import AppHelper
from Foundation import NSObject
import os

import sys
sys.path.append('./')
sys.path.append('/Library/Python/2.7/site-packages/lxml-3.3.1-py2.7-macosx-10.9-intel.egg')
from song_model import SongModel
from util import replace_tempo_map, replace_time_sig_map, \
    replace_marker_track, replace_arranger_track, import_track


import pkgutil
PyObjCTools.Signals.dumpStackOnFatalSignal()


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
    trackTextBox = Cocoa.objc.IBOutlet()
    trackTableView = Cocoa.objc.IBOutlet()
    trackOutlineView = Cocoa.objc.IBOutlet()
    tempomapCheckBox = Cocoa.objc.IBOutlet()
    timesigmapCheckBox = Cocoa.objc.IBOutlet()
    markertrackCheckBox = Cocoa.objc.IBOutlet()
    arrangertrackCheckBox = Cocoa.objc.IBOutlet()

    @Cocoa.objc.IBAction
    def timesigmap_(self, sender):
        self.timesigmap_enabled = sender.state()

    @Cocoa.objc.IBAction
    def markertrack_(self, sender):
        self.markertrack_enabled = sender.state()

    @Cocoa.objc.IBAction
    def arrangertrack_(self, sender):
        self.arrangertrack_enabled = sender.state()
    
    def init(self):
        self.src_song = None
        self.dst_song = None
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
            self.trackTextBox.setStringValue_(
                '\n'.join(self.src_song.song.track_names.keys()))
            self.trackTableView.reloadData()
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


    # NSTableViewDataSource
    def numberOfRowsInTableView_(self, tableView):
        print 'num rows'
        if not hasattr(self, 'src_song') or self.src_song == None:
            return 0
        else:
            return len(self.src_song.song.track_names.keys())

    # NSTableViewDelegate
    def tableView_viewForTableColumn_row_(self, tableView, tableColumn, row):
        print 'getting table view for row %i' % row
        # Get an existing cell with the MyView identifier if it exists
        result = tableView.makeViewWithIdentifier_owner_('MyView', self);
     
        # There is no existing cell to reuse so create a new one
        if (result == None):
            # Create the new NSTextField with a frame of the {0,0} with the width of the table.
            # Note that the height of the frame is not really relevant, because the row height will modify the height.
            result = Cocoa.NSTextField.alloc().initWithFrame_(Cocoa.NSMakeRect(0, 0, 100, 0))
     
            # The identifier of the NSTextField instance is set to MyView.
            # This allows the cell to be reused.
            result.setIdentifier_('MyView')
     
        # result is now guaranteed to be valid, either as a reused cell
        # or as a new cell, so set the stringValue of the cell to the
        # nameArray value at row
        result.setStringValue_(self.src_song.song.track_names.keys()[row])
     
        # Return the result
        return result

    # NSOutlineViewDataSource
    def outlineView_numberOfChildrenOfItem_(self, outlineView, item):
        print 'num children of %s' % item
        if item == None:
            if not hasattr(self, 'src_song') or self.src_song == None:
                return 0
            else:
                return len(self.src_song.song.track_names.keys())
        elif item in TRACK_OPTIONS:
            return 0
        else:
            return len(TRACK_OPTIONS)
    
    def outlineView_isItemExpandable_(self, outlineView, item):
        print 'Expandable?  %s' % item
        if item in TRACK_OPTIONS:
            print '168'
            return False
        else:
            print '171'
            return True
    
    def outlineView_child_ofItem_(self, outlineView, index, item):
        print 'Child?  %s' % item
        if item == None:
            print '174'
            return self.src_song.song.track_names.keys()[index]
        else:
            print '177'
            return TRACK_OPTIONS[index]
    
    #def outlineView_objectValueForTableColumn_byItem_(self, outlineView, tableColumn, item):
    #    print item
    #    print '184'
    #    return item


    def outlineView_viewForTableColumn_item_(self, outlineView, tableColumn, item):
        print 'view for %s' % item
        tcv = outlineView.makeViewWithIdentifier_owner_("MainCell", self)
        tcv.textField().setStringValue_(item)
        
        #NSImage* cellImage;
        #
        #if (HAS_KEY(item,@"children")) cellImage = [[NSWorkspace sharedWorkspace] iconForFileType:NSFileTypeForHFSTypeCode(kGenericFolderIcon)];
        #else cellImage = [[NSWorkspace sharedWorkspace] iconForFileType:NSFileTypeRegular];
        
        #[cellImage setSize:NSMakeSize(15.0, 15.0)];
        
        #tcv.imageView.image = cellImage;
        
        return tcv


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
