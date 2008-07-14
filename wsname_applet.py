#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gobject
import pango
import gtk
import gnome
import gnome.ui
import gnomeapplet
import bonobo
import bonobo.ui
import wnck
import gconf

from wsnamelet import aligned_window
from wsnamelet import wsnamelet_globals

 
#Uncomment to debug. If you aren't me, I bet you want to change the paths, too.
#import os
#new_stdout = open ("/home/munizao/hacks/googlesvn/wsnamelet/debug.stdout", "w")
#new_stderr = open ("/home/munizao/hacks/googlesvn/wsnamelet/debug.stderr", "w")
#os.dup2(new_stdout.fileno(), sys.stdout.fileno())
#os.dup2(new_stderr.fileno(), sys.stderr.fileno())

#Internationalize
import locale
import gettext
gettext.bindtextdomain('wsnamelet', '/usr/share/locale')
gettext.textdomain('wsnamelet')
locale.bindtextdomain('wsnamelet', '/usr/share/locale')
locale.textdomain('wsnamelet')
gettext.install('wsnamelet', '/usr/share/locale', unicode=1)

#screen = None

class WSNamePrefs(object):    
    def __init__(self, applet):
        self.applet = applet
        self.dialog = gtk.Dialog("Workspace Name Applet Preferences",
                                 None,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.dialog.set_border_width(10)
        self.width_check = gtk.CheckButton(label="Applet changes width to fit text.")
        self.width_check.connect("toggled", self.on_check_toggled)
        if self.applet.allow_width_change:
            self.width_check.set_active(True)
        width_spin_label = gtk.Label(_("Applet width in pixels:"))
        self.width_spin_button = gtk.SpinButton(gtk.Adjustment(lower=1, upper=300, step_incr=1))
        self.width_spin_button.set_value(self.applet.width)

        self.width_spin_button.connect("value_changed", self.on_width_spin_changed)
        width_spin_hbox = gtk.HBox()
        width_spin_hbox.pack_start(width_spin_label)
        width_spin_hbox.pack_start(self.width_spin_button)
        self.dialog.vbox.add(self.width_check)
        self.dialog.vbox.add(width_spin_hbox)

    def on_width_spin_changed(self, width_spin):
        self.applet.width = width_spin.get_value_as_int()
        self.applet.gconf_client.set_int(self.applet.gconf_key_width, self.applet.width)
        self.applet.label.set_size_request(self.applet.width, -1)
        self.applet.label.queue_resize()

    def on_check_toggled(self, event):
        self.applet.allow_width_change = self.width_check.get_active()
        self.applet.gconf_client.set_bool(self.applet.gconf_key_allow_width_change, self.applet.allow_width_change)
        self.width_spin_button.set_sensitive(not self.applet.allow_width_change)
        if self.applet.allow_width_change:
            self.applet.label.set_ellipsize(pango.ELLIPSIZE_NONE)
            self.applet.label.set_size_request(-1, -1)
        else:
            self.applet.label.set_ellipsize(pango.ELLIPSIZE_END)
            self.applet.label.set_size_request(self.applet.width, -1)
            

class WSNameEntryWindow(aligned_window.AlignedWindow):
    def __init__(self, applet):
        aligned_window.AlignedWindow.__init__(self, applet)
	self.applet = applet
	frame = gtk.Frame()
	frame.set_shadow_type(gtk.SHADOW_OUT)
        self.entry = gtk.Entry()
	frame.add(self.entry)
	self.add(frame)
        #self.set_modal(True) #Modal bad. No reason why we can't use toggle with entry window open
	#self.set_keep_above(True)
	
	self.set_default_size(0,0)
        self.entry.connect("activate", self._on_activate)
        self.entry.connect("key-release-event", self._on_key_release)

    def _on_activate(self, event):
        self.applet.toggle.set_active(False)
        self.applet.workspace.change_name(self.entry.get_text())

    def _on_key_release(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.toggle.set_active(False)
        

class WSNameApplet(gnomeapplet.Applet):
    _name_change_handler_id = None
    workspace = None
    
    def __init__(self):
        self.__gobject_init__()


    menu = """
        <popup name="button3">
            <menuitem name="Item 1" verb="Preferences" label="_Preferences"
                pixtype="stock" pixname="gtk-preferences"/>
            <menuitem name="Item 2" verb="About" label="_About"
                pixtype="stock" pixname="gtk-about"/>
        </popup>
    """

    def _display_about(self, widget, data):
        about = gnome.ui.About("Workspace Name Applet", 
                               wsnamelet_globals.version, 
                               "© 2006 - 2008 Alexandre Muñiz", 
                               "View and change the name of the current workspace.\n\nTo change the workspace name, click on the applet, type the new name, and press Enter.", 
                               ["Alexandre Muñiz"], [""])
        about.show()

    def _display_prefs(self, widget, data):
        self.prefs.dialog.show_all()
        self.prefs.dialog.run()
        self.prefs.dialog.hide()

    def init(self):
        self.gconf_path = "/apps/wsnamelet"
        self.gconf_client = gconf.client_get_default()
        self.add_preferences("/schemas" + self.gconf_path)
        self.gconf_dir = self.get_preferences_key()
        print self.gconf_dir
        self.gconf_client.add_dir(self.gconf_dir, gconf.CLIENT_PRELOAD_NONE)
        self.gconf_key_width = self.gconf_dir + "/width"
        self.gconf_key_allow_width_change = self.gconf_dir + "/allow_width_change"
        self.width = self.gconf_client.get_int(self.gconf_key_width) or 100
        if self.width < 30:
            self.width = 30

        self.allow_width_change = self.gconf_client.get_bool(self.gconf_key_width) or False
        self.toggle = gtk.ToggleButton()
	self.toggle.connect("toggled", self._on_toggled)
        self.toggle.connect("button-press-event", self._on_button_press)
	self.label = gtk.Label()
        if not self.allow_width_change:
            self.label.set_ellipsize(pango.ELLIPSIZE_END)
            self.label.set_size_request(self.width, -1)
	self.add(self.toggle)
	self.toggle.add(self.label)
	
        self.setup_menu(self.menu, 
                        [("Preferences", self._display_prefs), ("About", self._display_about)], 
                        None)

	self.screen = wnck.screen_get_default()
	self.screen.connect("active_workspace_changed", self._on_workspace_changed)
	self.entry_window = WSNameEntryWindow(self)

	self._name_change_handler_id = None

        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self.toggle, _("Click to change the name of the current workspace"))

        self.prefs = WSNamePrefs(self)
	return True	    

    def _on_toggled(self, event):
        if self.toggle.get_active():
            self.entry_window.positionWindow()            
            self.entry_window.show_all()
            self.entry_window.present()
	    self.entry_window.entry.set_text(self.workspace.get_name())
            self.entry_window.entry.set_position(-1)            
            self.entry_window.entry.select_region(0, -1)
            gobject.timeout_add(0, self.entry_window.entry.grab_focus)
            self.tooltips.disable()
        else:
            self.entry_window.hide()
            self.tooltips.enable()

    def _on_button_press(self, toggle, event):
        if event.button != 1:
            toggle.stop_emission("button-press-event")

    def _on_workspace_changed(self, event, old_workspace):
        if self.toggle.get_active():
            self.toggle.set_active(False)
	if (self._name_change_handler_id):
	    self.workspace.disconnect(self._name_change_handler_id)
        self.workspace = really_get_active_workspace(self.screen)
	self._name_change_handler_id = self.workspace.connect("name-changed", self._on_workspace_name_changed)
        self.show_workspace_name()

    def _on_workspace_name_changed(self, event):
	self.show_workspace_name()

    def show_workspace_name(self):
	self.label.set_text(self.workspace.get_name())
	self.show_all()


def really_get_active_workspace(screen):
    # This bit is needed because wnck is asynchronous.
    while gtk.events_pending():
        gtk.main_iteration() 
    return screen.get_active_workspace()

def wsn_factory_init(applet, iid):
    return applet.init()

gobject.type_register(WSNameApplet)
gnomeapplet.bonobo_factory("OAFIID:GNOME_WorkspaceName_Factory", 
			     WSNameApplet.__gtype__, 
			     "workspace name", "0", wsn_factory_init)
