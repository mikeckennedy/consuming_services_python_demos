import requests
from xml.etree import ElementTree
import os
import shutil


def main():
    mp3_files = get_episode_files('https://talkpython.fm/rss')
    for file in mp3_files[:3]:
        download_file(file, '/Users/screeencaster/Desktop/mp3s/')


def get_episode_files(url):
    resp = requests.get(url)
    xml_text = resp.text

    dom = ElementTree.fromstring(xml_text)

    return [
        enclosure_node.attrib['url']
        for enclosure_node in dom.findall('channel/item/enclosure')
    ]


def download_file(file, dest_folder):
    resp = requests.get(file, stream=True)
    resp.decode_content = True

    base_file = os.path.basename(file)
    dest_file = os.path.join(
        os.path.abspath(dest_folder),
        base_file)

    print("Downloading and saving " + base_file)

    with open(dest_file, 'wb') as fout:
        shutil.copyfileobj(resp.raw, fout)

if __name__ == '__main__':
    main()
