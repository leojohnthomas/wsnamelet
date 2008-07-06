#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gobject
import gtk
import gnome
import gnome.ui
import gnomeapplet
import bonobo
import bonobo.ui
import wnck

from wsnamelet import aligned_window
from wsnamelet import wsnamelet_globals

screen = None

def about_cb(widget, data):
    about = gnome.ui.About("Workspace Name Applet", wsnamelet_globals.version, "© 2006, 2007 Alexandre Muñiz", 
"View and change the name of the current workspace.\n\nTo change the workspace name, click on the applet, type the new name, and press Enter.", ["Alexandre Muñiz"], [""])
    about.show()



menu = """
    <popup name="button3">
	<menuitem name="Item 1" verb="About" label="About..."
	    pixtype="stock" pixname="gnome-stock-about"/>
    </popup>
"""

class WSNameEntryWindow(aligned_window.AlignedWindow):
    def __init__(self, applet):
        aligned_window.AlignedWindow.__init__(self, applet)
	self.applet = applet
	frame = gtk.Frame()
	frame.set_shadow_type(gtk.SHADOW_OUT)
        self.entry = gtk.Entry()
	frame.add(self.entry)
	self.add(frame)
        #self.set_modal(True)
	#self.set_keep_above(True)
	
	self.set_default_size(0,0)
        self.entry.connect("activate", self._onActivate)
	#self.entry.connect_after("changed", self._onEntryChanged)

    def _onActivate(self, event):
        self.applet.toggle.set_active(False)
        self.applet.workspace.change_name(self.entry.get_text())
        
    # was changing the workspace name here, which I think was a mistake.
    #def _onEntryChanged(self, event):



class WSNameApplet(gnomeapplet.Applet):
    _name_change_handler_id = None
    workspace = None
    
##     def __init__(self):
##         self.__gobject_init__()

    menu = """
        <popup name="button3">
            <menuitem name="Item 1" verb="About" label="About..."
                pixtype="stock" pixname="gnome-stock-about"/>
        </popup>
    """

    def init(self):
        self.toggle = gtk.ToggleButton()
	self.toggle.connect("toggled", self._onToggled)
        self.toggle.connect("button-press-event", self._onButtonPress)
	self.label = gtk.Label()
	self.add(self.toggle)
	self.toggle.add(self.label)
	self.setup_menu(self.menu, [("About", about_cb), ], None)
	self.screen = wnck.screen_get_default()
	self.screen.connect("active_workspace_changed", self._onWorkspaceChanged)
	self.entry_window = WSNameEntryWindow(self)
	self._name_change_handler_id = None

        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self.toggle, "Click to change the name of the current workspace")
	return True	    

    def _onToggled(self, event):
        if self.toggle.get_active():
            self.entry_window.positionWindow()            
            self.entry_window.show_all()
	    self.entry_window.entry.set_text(self.workspace.get_name())
            self.entry_window.entry.set_position(-1)            
            self.entry_window.entry.select_region(0, -1)
            self.entry_window.entry.grab_focus()
            self.tooltips.disable()
        else:
            self.entry_window.hide()
            self.tooltips.enable()

    def _onButtonPress(self, toggle, event):
        if event.button != 1:
            toggle.stop_emission("button-press-event")

    def _onWorkspaceChanged(self, event):
        if self.toggle.get_active():
            self.toggle.set_active(False)
	if (self._name_change_handler_id):
	    self.workspace.disconnect(self._name_change_handler_id)
        self.workspace = really_get_active_workspace(self.screen)
	self._name_change_handler_id = self.workspace.connect("name-changed", self._onWorkspaceNameChanged)
        self.showWorkspaceName()

    def _onWorkspaceNameChanged(self, event):
	self.showWorkspaceName()

    def showWorkspaceName(self):
	self.label.set_text(self.workspace.get_name())
	self.show_all()

def really_get_active_workspace(screen):
    # This bit is needed because wnck is asynchronous.
    while gtk.events_pending():
        gtk.main_iteration() 
    return screen.get_active_workspace()

def wsn_factory_init(applet, iid):
    return applet.init()

#To test in a standalone window, type "./wsname_applet.py run-in-window"
if len(sys.argv) == 2:
    if sys.argv[1] == "run-in-window":
	main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	main_window.set_title("Python Applet")
	main_window.connect("destroy", gtk.main_quit)
	app = WSNameApplet()
	wsn_factory_init(app, None)
	app.reparent(main_window)
	main_window.show_all()
	gtk.main()
	sys.exit()

gobject.type_register(WSNameApplet)
gnomeapplet.bonobo_factory("OAFIID:GNOME_WorkspaceName_Factory", 
			     WSNameApplet.__gtype__, 
			     "workspace name", "0", wsn_factory_init)
