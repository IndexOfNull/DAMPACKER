![Logo Image](https://i.imgur.com/7lUeUhm.png)

# DAMPACKER

DAMPACKER is a simple, but effective packer designed to make your modpack development workflow easier. It was originally made to assist with the development of [DAMPACK'D](https://github.com/IndexOfNull/DAMPACKD)

# Installation

Using DAMPACKER is fairly simple. Just follow the steps below and make sure you are using Python 3.6 or greater:

1. Install `requests` with `pip install requests==2.23.0` (this is the only non-standard python library)

2. Copy `dampacker.py` and `dampacker.json` into your modpack repository (this tool works best when you are tracking your pack in a Git repo)

3. Fill out the `dampacker.json` file with any override directories/files you want to include/exclude (globs should work but are not tested). You can also link mods that are not available on CurseForge here.

4. Open a terminal in your project and run `python dampacker.py` (you can add a `-s` flag to make a server install package)

# Important Notes

DAMPACKER should be intuitive to use, but there are some things to note.

- ***The working directory for profile builds will be deleted every time this tool is used unless specified otherwise***. Make sure that you set your build work directory to be a directory that *does not exist* and one that you will not do any work in yourself.

- *No directories are included by default*. You must manually specify include directores, though you shouldn't have too many.

- *Do not include your working directory* (you're asking for trouble)

- *You only have to touch the include field*. The exlude field will default to nothing, and the server include/exclude fields will default to the client include/exclude settings if omitted. External mod URLs can also be left blank if you have none.