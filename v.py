import requests
from bs4 import BeautifulSoup

url = 'https://downloads.raspberrypi.org/raspios_lite_armhf/images/'

def list_files(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if "raspios" in node.get('href')]

for file in list_files(url):
    print (file)
