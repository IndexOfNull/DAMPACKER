from os.path import abspath, relpath
import requests
import json
import os
import shutil
from glob import glob
import argparse
import re
import codecs

#####################
# Constants         #
#####################

BASE_URL = "https://addons-ecs.forgesvc.net/api/v2/addon/"
HEADERS = {'User-Agent': 'DAMPACKER'}

#############################
# CLI Arg Parsing / Setup   #
#############################

parser = argparse.ArgumentParser(description='Make a modpack!')

parser.add_argument("--server", "-s", action="store_true", help="Create a pack suited for manual installation/servers")
parser.add_argument("--config", "-c", type=str, default="dampacker.json", help=".json config file to read from")
parser.add_argument("--workdir", "-d", type=str, default="profilebuild", help="Working directory for profile building")
parser.add_argument("--output", "-o", type=str, default=None, help="Where to write the resulting .zip file")
parser.add_argument("--pack-only", action="store_true", default=False, help="Skip data fetching and downloading, useful if you made non-mod changes and want to repackage.\nYou should only use this if you've already built before. This also implies --no-predelete.")
parser.add_argument("--no-predelete", action="store_true", default=False, help="Prevent the program from predeleting the working directory. You generally don't need to use this.")

args = parser.parse_args()

if args.pack_only:
    args.no_predelete = True

server_pack = args.server
build_folder = args.workdir
overrides_folder = os.path.join(build_folder, "overrides")

with open("manifest.json", "r") as f:
    contents = f.read()
    manifest = json.loads(contents)

with open(args.config, "r") as f:
    contents = f.read()
    config = json.loads(contents)

if 'include' not in config:
    print("Include files not present. Please add them to your config")
    exit()

# fill in any missing config keys
config_defaults = {
    "exclude": [],
    "serverInclude": config['include'],
    "serverExclude": config['exclude'] if 'exclude' in config else [],
    "externalModUrls": []
}

for key in config_defaults.keys():
    if key not in config:
        config[key] = config_defaults[key]

#create a default output file name based on manifest name and version
if args.output is None:
    filtered_name = re.sub(r'[^\w\-. ]', '', manifest['name'])
    filtered_version = re.sub(r'[^\w\-. ]', '', manifest['version'])
    if server_pack:
        filtered_version += "-SERVER"
    output_zip = filtered_name + "-" + filtered_version + ".zip"
else:
    output_zip = args.output

print("Creating profile for {0} ({1})...\n".format(manifest['name'], manifest['version']))

# create working directory
if not os.path.exists(overrides_folder):
    os.makedirs(overrides_folder)
elif not args.no_predelete:
    print("Removing old profile working directory.")
    shutil.rmtree(build_folder)

#####################
# Data Download     #
#####################

# takes a project id and file id and returns a dictionary containing the file info
def get_file(project_id, file_id):
    resp = requests.get(BASE_URL + str(project_id) + "/file/" + str(file_id), headers=HEADERS)
    return resp.json()

def get_project(project_id):
    resp = requests.get(BASE_URL + str(project_id), headers=HEADERS)
    return resp.json()

def download_file(url, dest_dir):
    filename = url.split("/")[-1]
    print("Downloading {0}".format(filename))
    with requests.get(url) as r:
        with open(os.path.join(dest_dir, filename), "wb") as f:
            f.write(r.content)

def make_modlist(projects):
    html_template = "<html><body><ul>{0}</ul></body></html>"
    mod_entry = '<li><a href="{0}">{1} (by {2})</li>'
    final_str = ""

    for project in projects.values():
        final_str += mod_entry.format(project['websiteUrl'], project['name'], project['authors'][0]['name'])
    return html_template.format(final_str)

if not args.pack_only:
    files = manifest['files']
    projects = {} #used to construct a modlist.html later
    target_files = {}
    for i, file in enumerate(files): #first pass to gather data
        if file['required']:
            project_data = get_project(file['projectID'])
            file_data = get_file(file['projectID'], file['fileID'])

            target_files[file['projectID']] = file_data
            projects[file['projectID']] = project_data
            print("Gathering addon data... ({0}/{1})".format(i, len(files)))

    for project in projects.values():
        file_data = target_files[project['id']]
        required_deps = set([x['addonId'] for x in file_data['dependencies'] if x['type'] == 3]) #Construct a set out of the *required* dependency ids. Also addonID == projectID
        incompatible_addons = set([x['addonId'] for x in file_data['dependencies'] if x['type'] == 5])
        for dep in required_deps:
            if not dep in projects.keys():
                missing_project = get_project(dep)
                print("Warning! Required dependency for {0} not present in manifest! (missing project: {1})".format(project['name'], missing_project['name']))
        for addon in incompatible_addons:
            if addon in projects.keys():
                print("Critical! {0} is not compatible with {1}".format(project['name'], projects[addon]['name']))

    mods_path = os.path.join(overrides_folder, "mods")
    if len(config['externalModUrls']) > 0: #Always download external mods
        if not os.path.exists(mods_path): #Could be refactored
            os.makedirs(mods_path)

        print("\n## Downloading external mods... ##\n")
        for url in config['externalModUrls']:
            download_file(url, mods_path)

    if server_pack:
        if not os.path.exists(mods_path): #Could be refactored
            os.makedirs(mods_path)

        print("\n## Downloading CurseForge mods... ##\n")
        for file in target_files.values():
            download_file(file['downloadUrl'], mods_path)
    else:
        print("\n## Skipping CurseForge mods (clients will downloadthem themselves)... ##\n")

    #Write a modlist
    with codecs.open(os.path.join(build_folder, "modlist.html"), "w", "utf-8") as f: #gotta use codecs in case SOMEONE decides to use dumb unicode chars in their mod name
        f.write(make_modlist(projects))

#####################
# Packaging         #
#####################

# Returns a normalized list of paths
def process_path_list(path_list):
    files = []
    for path in path_list:
        if os.path.isdir(path):
            f = glob(os.path.join(path, "**/*.*"), recursive=True)
            files.extend([os.path.normpath(x) for x in f])
        elif os.path.isfile(path):
            files.append(os.path.normpath(path))
    return files

# Takes files from the current working directory and repackages them into the build directory
def package_files(files):
    for file in files:
        abs_path = os.path.abspath(file)
        rel_path = os.path.relpath(abs_path, os.getcwd())
        target_path = os.path.join(overrides_folder, rel_path)
        target_parent_path = os.path.abspath(os.path.join(target_path, os.pardir))
        if not os.path.exists(target_parent_path):
            os.makedirs(target_parent_path)
        shutil.copy(file, target_path)

#resolve include/exclude lists
include_files = set(process_path_list(config['include']))
exclude_files = set(process_path_list(config['exclude']))
include_files = include_files.difference(exclude_files)

server_include_files = set(process_path_list(config['serverInclude']))
server_exclude_files = set(process_path_list(config['serverExclude']))
server_include_files = server_include_files.difference(server_exclude_files)

#Copy all files, making directories as needed
if server_pack:
    package_files(server_include_files)
else:
    package_files(include_files)

shutil.copy("manifest.json", os.path.join(build_folder, "manifest.json")) #Copy the manifest

#####################
# ZIP Creation      #
#####################
zip_target = os.path.abspath(overrides_folder if server_pack else build_folder)
shutil.make_archive(".".join(output_zip.split('.')[:-1]), 'zip', zip_target, '.')
