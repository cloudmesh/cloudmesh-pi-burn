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
from cloudmesh.common.Tabulate import Printer

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# noinspection PyPep8
class Image(object):

    # self.directory: the folder where downloaded images are kept
    # self.image_name: the name of the image (or URL to fetch it from)
    # self.fullpath: the full path of the image, e.g.
    # /home/user/.cloudmesh/images/raspbian-2019.img

    def __init__(self):

        self.directory = os.path.expanduser('~/.cloudmesh/cmburn/images')
        self.cache = Path(os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))
        os.system('mkdir -p ' + self.directory)

        self.raspberry_images = {
            "lite": "https://downloads.raspberrypi.org/raspios_lite_armhf/images",
            "full": "https://downloads.raspberrypi.org/raspios_full_armhf/images"
        }
        # if name == 'latest':
        #    self.fullpath = self.directory + '/' + self.latest_version() + '.img'
        # else:
        #    self.fullpath = self.directory + '/' + self.image_name + '.img'

    def read_version_cache(self):
        data = yaml.load(readfile(self.cache), Loader=yaml.SafeLoader)
        return data


    @staticmethod
    def find(tag=['latest']):
        found = []
        data = Image.create_version_cache(refresh=False)
        for entry in data:
            match = True
            for t in tag:
                match = match and t in entry["tag"]
            if match:
                found.append(entry)
        return found

    @staticmethod
    def create_version_cache(refresh=False):

        data = {
            "lite": [],
            "full": []
        }
        cache = Path(os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))

        def fetch_kind(kind=None):
            print(f"finding {kind} repos ...", end="")
            image = Image()
            location = f"{image.raspberry_images[kind]}"
            repos = [location]

            latest = {
                'date': "1900-01-01"
            }
            for repo in repos:
                versions, downloads = Image.versions(repo)
                print("These images are available at")
                for version, download in zip(versions, downloads):
                    entry = {
                        "version": version,
                        "tag": version.replace("raspios_", "").replace("_armhf", ""),
                        "url": download,
                        "date": version.split("-", 1)[1],
                        "type": kind
                    }
                    data[kind].append(entry)
                    if entry["date"] >= latest['date']:
                        latest = dict(entry)
                        latest["tag"] = f"latest-{kind}"

                data[kind].append(latest)

        if refresh or not cache.exists():
            os.system("mkdir -p ~/.cloudmesh/cmburn")
            fetch_kind(kind="lite")
            fetch_kind(kind="full")
            writefile(cache, yaml.dump(data))

        data = readfile(cache)
        data = yaml.safe_load(readfile(cache))
        # convert to array
        result = data["lite"] + data["full"]
        return result

    @staticmethod
    def versions(repo):
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
                download = Image.find_image_zip(repo, line)
                d.append(download)
        return v, d

    @staticmethod
    def find_image_zip(repo, version):

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

    @staticmethod
    def latest_version(kind="lite"):
        data = Image().read_version_cache()

        url = data[kind]["latest"]['url']

        return os.path.basename(source_url)[:-4]

    @staticmethod
    def get_name(url):
        return os.path.basename(url).replace('.zip', '')


    def fetch(self, url=None, tag=None):
        """
        Download the image from the URL in self.image_name
        If it is 'latest', download the latest image - afterwards use
          cm-pi-burn image ls
          to get the name of the downloaded latest image.
        """

        if url is None:
            data = Image().create_version_cache(refresh=False)

            image = Image().find(tag=tag)

            if image is None:
                Console.error("No matching image found.")
                return ""
            elif len(image) > 1:
                Console.error("Too manay images found")
                print(Printer.write(image,
                                    order=["tag", "version"],
                                    header=["Tag", "Version"]))
                return ""

            image = image[0]

            image_path = Image().directory + "/" + Image.get_name(image["url"]) + ".img"


        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        os.chdir(self.directory)
        # get image URL metadata, including the name of the latest image after
        #   the 'latest' URL redirects to the URL of the actual image
        source_url = requests.head(image["url"], allow_redirects=True).url
        size = requests.get(image["url"], verify=False, stream=True).headers[
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

        os.system("wget -O {} {}".format(zip_filename, image["url"]))

        #   if latest:  # rename filename from 'latest' to the actual image name
        #        Path('raspbian_lite_latest').rename(zip_filename)

        print("Extracting {}".format(img_filename))
        self.unzip_image(zip_filename)
        Path(zip_filename).unlink()

    def unzip_image(self, zip_filename):
        """
        Unzip image.zip to image.img
        """
        image = Image()
        os.chdir(image.directory)
        # img_filename = zip_filename.replace('.zip', '.img')
        zipfile.ZipFile(zip_filename).extractall()

    def verify(self):
        """
        verify if the image is ok, use SHA
        """
        raise NotImplementedError

    def rm(self, image="lite"):
        """
        Delete a downloaded image
        """
        # tag = tag or "latest"
        # if tag == "latest":
        #   tag = latest_version(kind="lite")

        for ending in [".img", ".zip"]:
            try:
                Path(Path(self.directory) / Path(image + ending)).unlink()
            except Exception as e:
                pass

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
