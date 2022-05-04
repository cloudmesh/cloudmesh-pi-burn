import glob
import os
import textwrap
import zipfile
from pathlib import Path

import oyaml as yaml
import requests
import urllib3
from cloudmesh.burn.util import sha1sum
from cloudmesh.burn.util import sha256sum
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile, writefile
from cloudmesh.common.Shell import Shell
from cloudmesh.burn.util import os_is_windows

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Ubuntu:
    download = "https://ubuntu.com/download/raspberry-pi/thank-you"
    release = "https://cdimage.ubuntu.com/releases/"
    distribution = [
        {
            "version": "20.04.2&architecture=server-arm64+raspi",
            "date": "2021-02-01",
            "type": "ubuntu",
            "os": "ubuntu",
            "tag": "ubuntu-20.04.2-64-bit",
            "description": "Ubuntu Server 20.04.2 LTS 64-bit",
            "alt": f"{download}?version=20.04.2&architecture=server-arm64+raspi",
            "url": f"{release}/20.04.2/release/ubuntu-20.04.2-preinstalled-server-arm64+raspi.img.xz",
            "sha256": "31884b07837099a5e819527af66848a9f4f92c1333e3ef0693d6d77af66d6832"
            # check
            # echo "31884b07837099a5e819527af66848a9f4f92c1333e3ef0693d6d77af66d6832
            #      *ubuntu-20.04.2-preinstalled-server-arm64+raspi.img.xz" | shasum -a 256 --check
        },
        {
            "version": "20.04.2&architecture=server-armhf+raspi",
            "date": "2021-02-01",
            "type": "ubuntu",
            "os": "ubuntu",
            "tag": "ubuntu-20.04.2-32-bit",
            "description": "Ubuntu Server 20.04.2 LTS 32-bit",
            "alt": f"{download}?version=20.04.2&architecture=server-armhf+raspi",
            "url": f"{release}/20.04.2/release/ubuntu-20.04.2-preinstalled-server-armhf+raspi.img.xz",
            "sha256": "7b348d080648b8e36e1f29671afd973a0878503091b935b69828f2c7722dfb58"
            # check
            # echo "7b348d080648b8e36e1f29671afd973a0878503091b935b69828f2c7722dfb58
            #      *ubuntu-20.04.2-preinstalled-server-armhf+raspi.img.xz" | shasum -a 256 --check
        },

        {
            "version": "20.10&architecture=server-arm64+raspi",
            "date": "2021-02-01",
            "type": "ubuntu",
            "os": "ubuntu",
            "tag": "ubuntu-20.10-64-bit",
            "description": "Ubuntu Server 20.10 64-bit",
            "alt": f"{download}?version=20.10&architecture=server-arm64+raspi",
            "url": f"{release}/20.10/release/ubuntu-20.10-preinstalled-server-arm64+raspi.img.xz",
            "sha256": "73a98e83fbb6398f86902c7a83c826536f1afbd0be2d80cb0d7faa94ede33137"
            # check
            # echo "73a98e83fbb6398f86902c7a83c826536f1afbd0be2d80cb0d7faa94ede33137
            #      *ubuntu-20.10-preinstalled-server-arm64+raspi.img.xz" | shasum -a 256 --check
        },

        {
            "version": "20.10&architecture=server-armhf+raspi",
            "date": "2021-02-01",
            "type": "ubuntu",
            "os": "ubuntu",
            "tag": "ubuntu-20.10-32-bit",
            "description": "Ubuntu Server 20.10",
            "alt": f"{download}?version=20.10&architecture=server-armhf+raspi",
            "url": f"{release}/20.10/release/ubuntu-20.10-preinstalled-server-armhf+raspi.img.xz",
            "sha256": "941752f93313ba765069b48f38af18bbf961bebefcc9c4296a953cf1260f0fe1"
            # check
            # echo "941752f93313ba765069b48f38af18bbf961bebefcc9c4296a953cf1260f0fe1
            #      *ubuntu-20.10-preinstalled-server-armhf+raspi.img.xz" | shasum -a 256 --check
        },
        {
            "version": "20.10&architecture=desktop-arm64+raspi",
            "date": "2021-02-01",
            "type": "ubuntu",
            "os": "ubuntu",
            "tag": "ubuntu-desktop",
            "description": "Ubuntu Desktop 20.10 64-bit",
            "alt": f"{download}?version=20.10&architecture=desktop-arm64+raspi",
            "url": f"{release}/20.10/release/ubuntu-20.10-preinstalled-desktop-arm64+raspi.img.xz",
            "sha256": "2fa19fb53fe0144549ff722d9cd755d9c12fb508bb890926bfe7940c0b3555e8"
            # check
            # echo "2fa19fb53fe0144549ff722d9cd755d9c12fb508bb890926bfe7940c0b3555e8
            #      *ubuntu-20.10-preinstalled-desktop-arm64+raspi.img.xz" | shasum -a 256 --check
        },
    ]


# noinspection PyPep8
class Image(object):

    # self.directory: the folder where downloaded images are kept
    # self.image_name: the name of the image (or URL to fetch it from)
    # self.fullpath: the full path of the image, e.g.
    # /home/user/.cloudmesh/images/raspbian-2019.img

    def __init__(self):

        self.directory = os.path.expanduser('~/.cloudmesh/cmburn/images')
        self.cache = Path(os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))
        Shell.mkdir(self.directory)

        #
        # import pathlib
        # directory = pathlib.Path.home() / '.cloudmesh' / 'cmburn'
        # directory.mkdir(parents=True, exist_ok=True)

        self.raspberry_images = {
            "lite": "https://downloads.raspberrypi.org/raspios_lite_armhf/images",
            "full": "https://downloads.raspberrypi.org/raspios_full_armhf/images",
            "lite-32": "https://downloads.raspberrypi.org/raspios_lite_armhf/images",
            "full-32": "https://downloads.raspberrypi.org/raspios_full_armhf/images",
            "lite-64": "https://downloads.raspberrypi.org/raspios_lite_arm64/images/",
            "full-64": "https://downloads.raspberrypi.org/raspios_arm64/images/",
            "lite-legacy": "https://downloads.raspberrypi.org/raspios_oldstable_lite_armhf/images",
            "full-legacy": "https://downloads.raspberrypi.org/raspios_oldstable_armhf/images/"
        }
        # if name == 'latest':
        #    self.fullpath = self.directory + '/' + self.latest_version() + '.img'
        # else:
        #    self.fullpath = self.directory + '/' + self.image_name + '.img'

    def read_version_cache(self):
        """
        reads the image list cache from the default cache location

        :return:
        :rtype:
        """
        data = yaml.load(readfile(self.cache), Loader=yaml.SafeLoader)
        return data

    @staticmethod
    def find(tag=None):
        """
        finds image names in the image list with the given tags

        :param tag: list of strings
        :type tag: list
        :return: tag matiching images
        :rtype: dict
        """
        tag = tag or ['latest-lite']
        if not isinstance(tag, list):
            tag = [tag]
        found = []
        data = Image.create_version_cache(refresh=False)
        for entry in data:
            match = True
            for t in tag:
                match = match and t == entry["tag"]
            if match:
                found.append(entry)
        if len(found) == 0:
            return None
        else:
            return found

    @staticmethod
    def create_version_cache(refresh=False):
        """
        creates a cache of all released pi images

        :param refresh: reresd it from the Web if True
        :type refresh: bool
        :return: writes it into ~/.cloudmesh/cmburn/distributions.yaml
        :rtype: file
        """

        data = {
            "lite": [],
            "full": [],
            "lite-32": [],
            "full-32": [],
            "lite-64": [],
            "full-64": [],
            "lite-legacy": [],
            "full-legacy": []
        }
        cache = Path(os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))

        def fetch_kind(kind=None):
            print(f"finding {kind} repos ...")
            image = Image()
            location = f"{image.raspberry_images[kind]}"
            repos = [location]

            latest = {
                'date': "1900-01-01"
            }
            for repo in repos:
                versions, downloads = Image.versions(repo)
                for version, download in zip(versions, downloads):
                    entry = {
                        "version": version,
                        "tag": version.replace("raspios_", "").replace("_armhf", ""),
                        "url": download,
                        "date": version.split("-", 1)[1],
                        "type": kind,
                        "os": "raspberryos",
                    }
                    data[kind].append(entry)
                    if entry["date"] >= latest['date']:
                        latest = dict(entry)
                        latest["tag"] = f"latest-{kind}"

                data[kind].append(latest)

        if refresh or not cache.exists():
            print('Before mkdir')
            if os_is_windows():
                Shell.mkdir(path_expand("~/.cloudmesh/cmburn"))
            else:
                os.system(f'mkdir -p {path_expand("~/.cloudmesh/cmburn")}')
            print('After mkdir')
            fetch_kind(kind="lite")
            fetch_kind(kind="full")
            fetch_kind(kind="lite-32")
            fetch_kind(kind="full-32")
            fetch_kind(kind="lite-64")
            fetch_kind(kind="full-64")
            fetch_kind(kind="lite-legacy")
            fetch_kind(kind="full-legacy")
            writefile(cache, yaml.dump(data))

        data = readfile(cache)
        data = yaml.safe_load(readfile(cache))
        # convert to array
        result = data["lite"] + data["full"] + \
                 data["lite-32"] + data["full-32"] + \
                 data["lite-64"] + data["full-64"] + \
                 data["lite-legacy"] + data["full-legacy"] + \
                 Ubuntu.distribution

        return result

    @staticmethod
    def versions(repo=None):
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
    def find_image_zip(repo=None, version=None):
        url = f"{repo}/{version}/"

        result = requests.get(url, verify=False)
        lines = result.text.split(' ')
        for line in lines:
            if ('.zip"' in line) or (".xz" in line) and "</td>" in line:
                line = line.split('href="')[1]
                line = line.split('"')[0]
                link = f"{repo}/{version}/{line}"
                return link
        return None

    @staticmethod
    def latest_version(kind="lite"):
        data = Image().read_version_cache()

        source_url = data[kind]["latest"]['url']

        return os.path.basename(source_url)[:-4]

    @staticmethod
    def get_name(url):
        return os.path.basename(url).replace('.zip', '').replace('.xz', '')

    def download_file(self, url=None, filename=None):
        if os_is_windows:
            os.system(f"curl -o {filename} {url}")
        else:
            os.system(f'wget -O {filename} {url}')

    # noinspection PyBroadException
    def fetch(self, url=None, tag=None, verify=True):
        """
        Download the image from the URL in self.image_name
        If it is 'latest', download the latest image - afterwards use
          cm-pi-burn image ls
          to get the name of the downloaded latest image.
        """

        if url is None:
            data = Image().create_version_cache(refresh=False)  # noqa: F841

            image = Image().find(tag=tag)

            if image is None:
                Console.error("No matching image found.")
                return None
            elif len(image) > 1:
                Console.error("Too many images found")
                print(Printer.write(image,
                                    order=["tag", "version"],
                                    header=["Tag", "Version"]))
                return None

            image = image[0]

            # image_path = Image().directory + "/" + Image.get_name(image[
            # "url"]) + ".img"

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        os.chdir(self.directory)
        # get image URL metadata, including the name of the latest image after
        #   the 'latest' URL redirects to the URL of the actual image

        if "ubuntu" in image["url"]:
            source_url = requests.head(image["url"], allow_redirects=True).url
            size = requests.get(image["url"], verify=False, stream=True).headers['Content-length']

            xz_filename = os.path.basename(source_url)
            img_filename = xz_filename.replace('.xz', '')
            img_file = Path(Path(self.directory) / Path(img_filename))
            # xz_file = Path(Path(self.directory) / Path(xz_filename))

            print(f"Downloading {xz_filename}")

            os.chdir(path_expand("~/.cloudmesh/cmburn/images"))

            if os.path.exists(img_filename):
                print()
                Console.warning(f"The file is already downloaded. Found at:\n\n"
                                f"    {img_file}\n")
                return img_file

            self.download_file(url=image["url"], filename=xz_filename)

            print(f"Extracting {img_filename}")
            self.unzip_image(xz_filename)
            try:
                Path(xz_filename).unlink()
            except:  # noqa: E722
                pass
            return img_filename

        else:
            source_url = requests.head(image["url"], allow_redirects=True).url
            size = requests.get(image["url"], verify=False, stream=True).headers['Content-length']
            zip_filename = os.path.basename(source_url)
            img_filename = zip_filename.replace('.zip', '.img')
            img_filename = zip_filename.replace('.img.xz', '.img')
            sha1_filename = zip_filename + '.sha1'
            sha256_filename = zip_filename + '.sha256'

            print(f"Downloading {zip_filename}")

            img_file = Path(Path(self.directory) / Path(img_filename))
            zip_file = Path(Path(self.directory) / Path(zip_filename))

            # sha1_file = Path(Path(self.directory) / Path(sha1_filename))
            # sha256_file = Path(Path(self.directory) / Path(sha256_filename))

            # cancel if image already downloaded
            if os.path.exists(img_filename):
                print()
                Console.warning(f"The file is already downloaded. Found at:\n\n"
                                f"    {img_file}\n")
                return img_file

            # download the image, unzip it, and delete the zip file
            image['sha1'] = image['url'] + ".sha1"
            image['sha256'] = image['url'] + ".sha256"
            if verify:
                self.download_file(url=image["sha1"], filename=sha1_filename)
                self.download_file(url=image["sha256"], filename=sha256_filename)

            self.download_file(url=image["url"], filename=zip_filename)

            if verify:
                sha1 = sha1sum(zip_file)
                sha256 = sha256sum(zip_filename)

                f_sha1 = readfile(sha1_filename).split(" ")[0]
                f_sha256 = readfile(sha256_filename).split(" ")[0]

                if f_sha1 == sha1:
                    Console.ok("SHA1 is ok")
                if f_sha256 == sha256:
                    Console.ok("SHA256 is ok")

            zip_size = os.path.getsize(zip_file)
            if int(size) != zip_size:
                Console.error(f"Repository reported zip size {size} does not equal "
                              f"download size {zip_size}. Please try again.")
                return None

            #   if latest:  # rename filename from 'latest' to the actual image name
            #        Path('raspbian_lite_latest').rename(zip_filename)

            print(f"Extracting {img_filename}")
            self.unzip_image(zip_filename)
            try:
                Path(zip_filename).unlink()
            except:
                pass
            return img_filename

    def unzip_image(self, zip_filename=None):
        """
        Unzip image.zip to image.img
        """
        image = Image()
        os.chdir(image.directory)
        # img_filename = zip_filename.replace('.zip', '.img')
        if ".zip" in zip_filename:
            zipfile.ZipFile(zip_filename).extractall()
        elif ".xz" in zip_filename or ".gz" in zip_filename:

            os.system(f"unxz {zip_filename}")
            # with tarfile.open(zip_filename) as f:
            #   content = f.extractall()

        else:
            raise ValueError("unkown zip format")

    def verify(self):
        """
        verify if the image is ok, use SHA
        """
        raise NotImplementedError

    # noinspection PyBroadException
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
            except Exception as e:  # noqa: F841
                pass
        return self.names()

    def ls(self):
        """
        List all downloaded images
        """
        images_dir = Path(self.directory)
        images = [str(x).replace(self.directory + '/', '')  # .replace('.img', '')
                  for x in images_dir.glob('*.img')]

        banner(f'Available Images in {self.directory}')

        print(textwrap.indent('.img\n'.join(images), prefix="    * "))
        print()
        return self.names()

    # noinspection PyBroadException
    def clear(self):
        """
        Delete all downloaded images

        TODO: not tested
        """
        self.ls()
        images_dir = Path(self.directory)

        for name in self.names():
            try:
                path = Path(Path(self.directory) / Path(name))
                print(path)
                path.unlink()

            except Exception as e:  # noqa: F841
                pass

        return self.names()

    def names(self):
        images_dir = Path(self.directory)
        return glob.glob(f"{images_dir}/*.img") + glob.glob(f"{images_dir}/*.zip")
