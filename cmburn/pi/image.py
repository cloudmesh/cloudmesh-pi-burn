#
# Example image link
#
# https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-09-30/2019-09-26-raspbian-buster-lite.zip

import requests
import os
from pathlib import Path
import zipfile
import wget
import oyaml as yaml

from cmburn.pi.util import readfile, writefile
from cmburn.pi import columns, lines

from cmburn.pi.util import WARNING

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Image(object):

    # self.directory: the folder where downloaded images are kept
    # self.image_name: the name of the image (or URL to fetch it from)
    # self.fullpath: the full path of the image, e.g. /home/user/.cloudmesh/images/raspbian-2019.img

    def __init__(self, name="latest"):
        self.directory = os.path.expanduser('~/.cloudmesh/cmburn/images')
        self.cache = Path(
            os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))
        os.system('mkdir -p ' + self.directory)
        self.image_name = name
        self.fullpath = self.directory + '/' + self.image_name + '.img'

    def version_cache_create(self, refresh=False):
        data = []

        if refresh or not self.cache.exists():
            os.system("mkdir -p ~/.cloudmesh/cmburn")
            print("finding repos ...", end="")
            repos = ["https://downloads.raspberrypi.org/raspbian_lite/images/"]
            for repo in repos:
                versions, downloads = Image().versions(repo)
                print("These images are available at")
                for version, download in zip(versions, downloads):
                    print("{}: {}".format(version, download))
                    data.append({version: download})
            writefile(self.cache, yaml.dump(data))
        else:
            data = yaml.load(readfile(self.cache), Loader=yaml.SafeLoader)
            for entry in data:
                version = list(entry.keys())[0]
                download = entry[version]
                print("{}: {}".format(version, download))


    def version_cache_read(self):
        data = yaml.load(readfile(self.cache), Loader=yaml.SafeLoader)
        return data

    def versions(self, repo):
        """
        Fetch and list available image versions and their download URLs
        """
        # image locations
        #
        # https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-09-30/

        #
        # versions can be found with https://downloads.raspberrypi.org/raspbian_lite/images/
        #

        result = requests.get(repo, verify=False)
        lines = result.text.split(' ')
        d = []
        v = []
        for line in lines:
            if 'href="' in line and "</td>" in line:
                line = line.split('href="')[1]
                line = line.split('/')[0]
                v.append(line)
                download = self.find_image_zip(line)
                d.append(download)
        return v, d

    def find_image_zip(self, version):

        url = "https://downloads.raspberrypi.org/raspbian_lite/images/{}/".format(version)

        result = requests.get(url, verify=False)
        lines = result.text.split(' ')
        v = []
        for line in lines:
            if '.zip"' in line and "</td>" in line:
                line = line.split('href="')[1]
                line = line.split('"')[0]
                link = "https://downloads.raspberrypi.org/raspbian_lite/images/{}/{}".format(version, line)
                return link
        return None


    def fetch(self):
        """
        Download the image from the URL in self.image_name
        If it is 'latest', download the latest image - afterwards use
          cm-pi-burn image ls
          to get the name of the downloaded latest image.
        """

        latest = False
        if self.image_name == 'latest':
            latest = True
            self.image_name = "https://downloads.raspberrypi.org/raspbian_lite_latest"
        debug = True

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        os.chdir(self.directory)
        # get image URL metadata, including the name of the latest image after
        #   the 'latest' URL redirects to the URL of the actual image
        source_url = requests.head(self.image_name, allow_redirects=True).url
        size = requests.get(self.image_name, verify=False, stream=True).headers[
            'Content-length']
        zip_filename = os.path.basename(source_url)
        img_filename = zip_filename.replace('.zip', '.img')

        print ("Downloading {}".format(zip_filename))

        # cancel if image already downloaded
        if os.path.exists(img_filename):
            WARNING("file already downloaded. Found at:",
                    Path(Path(self.directory) / Path(img_filename)))
            return

        # cancel if image already downloaded
        img_file = Path(Path(self.directory) / Path(img_filename))
        if os.path.isfile(img_file):
            WARNING("file already downloaded. Found at:",
                    Path(Path(self.directory) / Path(zip_filename)))
            return

        # download the image, unzip it, and delete the zip file
        print(self.image_name)
        os.system("wget -O {} {}".format(zip_filename, self.image_name))

        #   if latest:  # rename filename from 'latest' to the actual image name
        #        Path('raspbian_lite_latest').rename(zip_filename)

        print("Extracting {}".format(img_filename))
        self.unzip_image(zip_filename)
        Path(zip_filename).unlink()

    def unzip_image(self, zip_filename):
        """
        Unzip image.zip to image.img
        """
        os.chdir(self.directory)
        img_filename = zip_filename.replace('.zip', '.img')
        zipfile.ZipFile(zip_filename).extractall()

    def verify(self):
        # verify if the image is ok, use SHA
        raise NotImplementedError

    def rm(self):
        """
        Delete a downloaded image (the one named self.image_name)
        """
        Path(Path(self.directory) / Path(self.image_name + '.img')).unlink()

    def ls(self):
        """
        List all downloaded images
        """
        images_dir = Path(self.directory)
        images = [str(x).replace(self.directory + '/', '').replace('.img', '')
                  for x in images_dir.glob('*.img')]

        print('Available images in', self.directory)
        print(columns * '=')
        print('\n'.join(images))

