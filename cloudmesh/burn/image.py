import os
import textwrap
import zipfile
from pathlib import Path

import oyaml as yaml
import requests
import urllib3

from cloudmesh.burn.util import readfile, writefile
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# noinspection PyPep8
class Image(object):

    # self.directory: the folder where downloaded images are kept
    # self.image_name: the name of the image (or URL to fetch it from)
    # self.fullpath: the full path of the image, e.g.
    # /home/user/.cloudmesh/images/raspbian-2019.img

    def __init__(self, name="latest"):
        name = name or "latest"
        self.directory = os.path.expanduser('~/.cloudmesh/cmburn/images')
        self.cache = Path(
            os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))
        os.system('mkdir -p ' + self.directory)
        self.image_name = name

        self.raspberry_lite_images = \
            "https://downloads.raspberrypi.org/raspios_lite_armhf/images"
        self.raspberry_full_images = \
            "https://downloads.raspberrypi.org/raspios_full_armhf/images"

        if name == 'latest':
            self.fullpath = self.directory + '/' + self.latest_version() + '.img'
        else:
            self.fullpath = self.directory + '/' + self.image_name + '.img'


    def version_cache_create(self, refresh=False):
        # not used
        # bug only for lite, needs repo as parameter
        data = []

        if refresh or not self.cache.exists():
            os.system("mkdir -p ~/.cloudmesh/cmburn")
            print("finding repos ...", end="")
            repos = [self.raspberry_lite_images]
            for repo in repos:
                versions, downloads = Image().versions(repo)
                print(" These images are available at")
                for version, download in zip(versions, downloads):
                    entry = {
                        "version": version,
                        "url": download,
                        "date": version.split("-", 1)[1]
                    }
                    print (entry)
                    data.append(entry)
            writefile(self.cache, yaml.dump(data))
        else:
            data = yaml.load(readfile(self.cache), Loader=yaml.SafeLoader)
            for entry in data:
                version = list(entry.keys())[0]
                download = entry[version]
                print(f"{version}: {download}")

    def version_cache_read(self):
        data = yaml.load(readfile(self.cache), Loader=yaml.SafeLoader)
        return data

    def versions(self, repo):
        """
        Fetch and list available image versions and their download URLs
        """

        result = requests.get(repo, verify=False)
        lines = result.text.split(' ')
        d = []
        v = []
        for line in lines:
            if 'href="' in line and "</td>" in line:
                line = line.split('href="')[1]
                line = line.split('/')[0]
                v.append(line)
                download = self.find_image_zip(repo, line)
                d.append(download)
        return v, d

    def find_image_zip(self, repo, version):

        url = f"{repo}/{version}/"

        result = requests.get(url, verify=False)
        lines = result.text.split(' ')
        for line in lines:
            if '.zip"' in line and "</td>" in line:
                line = line.split('href="')[1]
                line = line.split('"')[0]
                link = f"{repo}/{version}/{line}"
                return link
        return None

    def latest_version(self):
        # bug must read from ~/.cloudmesh/cmburn/distributions.yaml
        source_url = requests.head(
            f"{self.raspberry_lite_images}/raspios_lite_armhf-2021-01-12/2021-01-11-raspios-buster-armhf-lite.zip",
            allow_redirects=True).url
        return os.path.basename(source_url)[:-4]

    def fetch(self):
        """
        Download the image from the URL in self.image_name
        If it is 'latest', download the latest image - afterwards use
          cm-pi-burn image ls
          to get the name of the downloaded latest image.
        """

        if self.image_name == 'latest':
            self.image_name = f"{self.raspberry_lite_images}/raspios_lite_armhf-2021-01-12/2021-01-11-raspios-buster-armhf-lite.zip"

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

        print("Downloading {}".format(zip_filename))

        img_file = Path(Path(self.directory) / Path(img_filename))
        zip_file = Path(Path(self.directory) / Path(zip_filename))

        # cancel if image already downloaded
        if os.path.exists(img_filename):
            print()
            Console.warning(f"The file is already downloaded. Found at:\n\n"
                            f"    {img_file}\n")
            return

        # cancel if image already downloaded
        if os.path.isfile(str(img_file)):
            print()
            Console.warning(f"The file is already downloaded. Found at:\n\n"
                            "    {zip_file}\n")

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
        # img_filename = zip_filename.replace('.zip', '.img')
        zipfile.ZipFile(zip_filename).extractall()

    def verify(self):
        """
        verify if the image is ok, use SHA
        """
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
        # print(columns * '=')

        banner('Available Images')

        print(textwrap.indent('\n'.join(images), prefix="    * "))
        print()
