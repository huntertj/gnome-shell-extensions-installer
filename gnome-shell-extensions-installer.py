#!/usr/bin/env python3
import argparse
import requests
import re
import json
import os.path
import xmltodict
from pathlib import Path
from zipfile import ZipFile

extensions_site = "https://extensions.gnome.org"
extensions_path = str(Path.home()) + "/.local/share/gnome-shell/extensions/"

parser = argparse.ArgumentParser(description='Download and install gnome-shell extension from ' + extensions_site)
parser.add_argument('-e', '--extensionid',
                    required=True,
                    action='store',
                    help='the extension id from the url in extensions.gnome.org')
parser.add_argument('-i', '--infoonly',
                    action='store_true',
                    help='provides extra info about the extension without downloading')
args = parser.parse_args()
extension_id = args.extensionid

def def_get_extension_info(extensions_site, extension_id):
    url = extensions_site + '/' + '/extension-info/?pk=' + extension_id
    r = requests.get(url, allow_redirects=True)
    # print(_extension_info)
    # print(_extension_info["name"]) # name, uuid, creator, pk, description, link, shell_version_map["3.28"]["version"]
    try: 
        json.loads(r.content)["uuid"]
    except:
        raise RuntimeError("Extension " + extension_id + " doesn't exist ")
    return json.loads(r.content)

def get_download_url(gnome_version, extensions_site, extension_info):
    try:
        version_for_gnome = str(extension_info["shell_version_map"][gnome_version]["pk"])
    except KeyError:
        raise RuntimeError("Extension doesn't exist for Gnome " + gnome_version )
    return extensions_site + '/download-extension/' + extension_info["uuid"] + '.shell-extension.zip?version_tag=' + version_for_gnome

def get_download_uuid(extension_info):
    return extension_info
    
def getFilename_fromCd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
        return fname[0]

def download_extension(download_url, download_uuid):
    r = requests.get(download_url, allow_redirects=True)
    filename = getFilename_fromCd(r.headers.get('content-disposition'))
    filename = extensions_path + download_uuid + ".zip"
    open(filename, 'wb').write(r.content)
    with ZipFile(filename, 'r') as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall(extensions_path + download_uuid)

with open('/usr/share/gnome/gnome-version.xml') as fd:
    doc = xmltodict.parse(fd.read())
    doc['gnome-version']['platform']
    gnome_version=(doc['gnome-version']['platform']+'.'+doc['gnome-version']['minor'])

extension_info = def_get_extension_info(extensions_site, extension_id)
download_url = get_download_url(gnome_version, extensions_site, extension_info)
download_uuid = extension_info["uuid"]

if args.infoonly:
    print(download_uuid)
    print(extension_info["description"])
else:
    print("Downloading and installing " + download_uuid + " into " + extensions_path)
    download_extension(download_url, download_uuid)
