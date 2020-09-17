# tmpfiles.org uploader

Python + GTK3 study project. Using glade editor to generate the ui file. Then using Gtk.Template to load the file and wire up the components.

## Usage

Just click on the paste button to upload the clipboard image to tempfiles.org or click on the file picker button to upload an image.

When the upload is done, the direct url will be on the clipboard.

## To install GTK

https://pygobject.readthedocs.io/en/latest/getting_started.html

## Then install local dependencies

`pip install -r requirements.txt`

## TODO

- parameterize `max_minutes` and `max_views`
- maybe add some progress bar
- maybe add a completion audio alert