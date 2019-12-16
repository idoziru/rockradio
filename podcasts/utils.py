import os
from datetime import datetime
import time
from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup
from django.conf import settings


def get_extension(filename: str) -> str:
    """
    Returns
        str: file extansion as .mp3, .pdf and so on.
    """
    filename = os.path.splitext(filename)[1]

    return filename.split("?")[0]  # cur averything adter ? .mp3?v=23


def get_uniq_id() -> str:
    """
    Each file mast have uniq id. Generated from epoch time. It give uniq number
    each time when we upload one file. It needs to delete this file after
    delete Model.object or any other manipulations.
    """
    file_id = str(time.time()).replace(".", "")
    return file_id


def make_filename(filename: str) -> str:
    """Helps to re-name files by using uniq id and current file extansion."""
    file_id = get_uniq_id()
    return "{0}{1}".format(file_id, get_extension(filename))


def get_podcast_folder(podcast) -> str:
    if podcast.folder_name:
        return podcast.folder_name
    return podcast.slug


def upload_podcast_files(podcast, filename: str) -> str:
    filename = make_filename(filename)
    podcast_folder = get_podcast_folder(podcast)
    return os.path.join(podcast_folder, filename)


def folder_path_new_episode(podcast_slug: str):
    path = os.path.join(podcast_slug, datetime.now().strftime("%Y/%m/%d"))
    return path


def folder_path_existing_episode(podcast_slug: str, pub_date):
    path = os.path.join(podcast_slug, pub_date.strftime("%Y/%m/%d"))
    return path


def upload_episode_files(episode, filename: str) -> str:
    """Upload file to defined podcast folder and use path from current date.

    Returns
        str: path to episode folder,
             for example 2capitals/2019/01/14/15492237901362188.mp3
    """
    path = folder_path_new_episode(episode.podcast.slug)
    filename = make_filename(filename)
    return os.path.join(path, filename)


def get_podcast_xml(url: str):
    return BeautifulSoup(urlopen(url), "xml").channel


def get_episodes_xml(url: str) -> list:
    return BeautifulSoup(urlopen(url), "xml").find_all("item")


def text_from_tag(xml, tag: str) -> str:
    if xml.find(tag):
        return xml.find(tag).text
    return "-" * 5


def tag_attrs(xml, tag: str, atr: str) -> str:
    if xml.find(tag):
        return xml.find(tag).attrs[atr]
    return "-" * 5


def download_file(folder: str, url: str) -> str:
    folder_full_path = os.path.join(settings.MEDIA_ROOT, folder)
    os.makedirs(folder_full_path, exist_ok=True)
    filename = make_filename(os.path.basename(url))
    file_path = os.path.join(folder_full_path, filename)
    urlretrieve(url, file_path)
    return os.path.join(folder, filename)


def is_explicit_to_bool(explicit: str) -> bool:
    if explicit.lower() == "yes":
        return True
    return False
