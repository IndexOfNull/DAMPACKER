![Logo Image](https://i.imgur.com/7lUeUhm.png)

# DAMPACKER

DAMPACKER is a simple, but effective packer designed to make your modpack development workflow easier. It was originally made to assist with the development of [DAMPACK'D](https://github.com/IndexOfNull/DAMPACKD)

# Installation

Using DAMPACKER is fairly simple. Just follow the steps below and make sure you are using Python 3.6 or greater:

1. Install `requests` with `pip install requests==2.23.0` (2.23.0 is the version I used, but the most recent should work. This is also the only non-standard python library)

2. Copy `dampacker.py` and `dampacker.json` into your modpack repository. This tool assumes that you are keeping track of override files separately from your pack installation. These files should be in the same directory as your `config`, `scripts`, `resources...` override folders.

3. Grab your pack's `manifest.json` file and copy it into the same directory as `dampacker.py`. DAMPACKER will not automatically generate a manifest for you, so you must get that from CurseForge (Export profile -> Only check mods -> Copy the manifest out of the resulting .zip)

Your file structure should end up looking something like this:
```
+--DAMPACKD (your pack repo)
  | config
  | scripts
  | resources
  | ... (more overrides)
  | dampacker.py
  | dampacker.json
  | manifest.json (from CurseForge)
  | ... (more miscellaneous directories: README, TODO, etc.)
```

4. Fill out the `dampacker.json` file with any override directories/files you want to include/exclude (globs should work but are not tested). You can also link mods that are not available on CurseForge here (they must be direct links to .jar files.) You do not need to include your `manifest.json` (it will be included automatically.)

5. Open a terminal in your project and run `python dampacker.py` (you can add a `-s` flag to make a server install package)

# Important Notes

DAMPACKER should be intuitive to use, but there are some things to note.

- ***The working directory for profile builds will be deleted every time this tool is used unless specified otherwise***. Make sure that you set your build work directory to be a directory that *does not exist* and one that you will not do any work in yourself.

- *No directories are included by default*. You must manually specify include directores, though you shouldn't have too many.

- *Do not include your working directory* (you're asking for trouble)

- *You only have to touch the include field*. The exlude field will default to nothing, and the server include/exclude fields will default to the client include/exclude settings if omitted. External mod URLs can also be left blank if you have none.

# Caveats

- DAMPACKER does not make any effort to cache mod data or mod binaries. This means that you will be pulling data from CurseForge *every* time you run a build. This should not normally be a problem, but large packs may want to take care not to spam CurseForge with too many requests (each mod in your manifest entails 2 HTTP requests)

- It is currently not possible to have client/server only mods. There is not a great way of doing this; it would probably have to be manually entering mod IDs into the `dampacker.json` file.
