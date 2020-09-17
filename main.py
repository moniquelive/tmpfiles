import logging
import os
import sys
import tempfile
import threading
from typing import Optional

import gi
import requests

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gio, Gtk, GLib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)


@Gtk.Template.from_file('main.glade')
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    paste_btn: Gtk.Button = Gtk.Template.Child()
    file_dlg_btn: Gtk.FileChooserDialog = Gtk.Template.Child()
    main_img: Gtk.Image = Gtk.Template.Child()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.file_dlg_btn.connect('file-set', self.file_set)
        self.paste_btn.connect('clicked', self.paste)

    def file_set(self, dlg: Gtk.FileChooserDialog):
        self.main_img.set_from_file(dlg.get_filename())
        self.transmit()

    def paste(self, *args):
        image = self.clipboard.wait_for_image()
        if image is not None:
            self.main_img.set_from_pixbuf(image)
            self.transmit()

    def update_ui(self, enabled):
        self.paste_btn.set_sensitive(enabled)
        self.file_dlg_btn.set_sensitive(enabled)

    def transmit(self):
        self.update_ui(False)
        thread = threading.Thread(target=self.transmit_async,
                                  args=[self.clipboard,
                                        self.main_img.get_pixbuf(),
                                        self.update_ui])
        thread.daemon = True
        thread.start()

    @staticmethod
    def transmit_async(clipboard, image, update_ui):
        filename = tempfile.NamedTemporaryFile().name
        try:  # depends on your Gdk version...
            image.save(filename, "jpeg", [], [])
        except:
            image.savev(filename, "jpeg", [], [])
        logger.debug("uploading %s", filename)
        r = requests.post(
            "https://tmpfiles.org/?upload",
            data={'max_minutes': 60, 'max_views': 0},
            files={'input_file': (os.path.basename(filename), open(filename, "rb"))},
            allow_redirects=False,
            timeout=(10, 30)
        )
        upload_path = r.headers['location'].replace('/download/', '/dl/')
        logger.debug("transmitted %s", upload_path)
        GLib.idle_add(clipboard.set_text, "https://tmpfiles.org" + upload_path, -1)
        GLib.idle_add(update_ui, True)


class Application(Gtk.Application):
    window: Optional[Gtk.ApplicationWindow] = None

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id='com.moniquelive.tmpfiles',
            flags=Gio.ApplicationFlags.FLAGS_NONE,
            **kwargs)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", lambda a, p: self.quit())
        self.add_action(action)

    def do_activate(self):
        if not self.window:
            self.window = MainWindow(application=self, title="tmpfiles.org")
        self.window.present()


if __name__ == '__main__':
    app = Application()
    app.run(sys.argv)
