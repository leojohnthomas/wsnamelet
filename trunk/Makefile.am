serverdir       = $(libdir)/bonobo/servers
server_in_files = GNOME_WorkspaceNameApplet.server.in
server_DATA     = $(server_in_files:.server.in=.server)

$(server_in_files): $(server_in_files:.server.in=.server.in.in)
	sed -e "s|\@LIBEXECDIR\@|$(libexecdir)|" $< > $@


@INTLTOOL_SERVER_RULE@


libexec_SCRIPTS = wsname_applet.py

wsnameletdir = $(pythondir)/wsnamelet

wsnamelet_PYTHON = 		\
	wsname_applet.py            \
	wsnamelet_globals.py    \
	aligned_window.py       \
        __init__.py


pixmapsdir = $(datadir)/pixmaps
pixmaps_DATA = wsnamelet.png

DISTCLEANFILES =                \
	$(server_DATA)	        \
	GNOME_WorkspaceNameApplet.server.in \
        intltool-extract        \
        intltool-merge          \
        intltool-update         \
        po/Makefile.in          \
        po/.intltool-merge-cache



EXTRA_DIST =  			\
	$(pixmaps_DATA)		\
        intltool-update.in      \
        intltool-extract.in     \
        intltool-merge.in       \
	GNOME_WorkspaceNameApplet.server.in.in \
        po/Makefile.in.in \
	po/POTFILES.in

