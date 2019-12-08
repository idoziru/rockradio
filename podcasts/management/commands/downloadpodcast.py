import os
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from dateutil import parser as dateparser
from django.core.management.base import BaseCommand
from podcasts.utils import (
    text,
    download_file,
    old_episode_folder_path,
    get_podcast_xml,
    get_episodes_xml,
    attrs,
    is_explicit,
)
from podcasts.models import Podcast, Episode


# URL = "https://podster.fm/rss.xml?pid=36066"


def create_podcast(podcast_xml, options) -> Podcast:
    podcast_folder = os.path.join(options["slug"])
    podcast = Podcast.objects.create(
        title=text(podcast_xml, "title"),
        slug=options["slug"],
        folder_name=options["slug"],
        link=text(podcast_xml, "link"),
        language=text(podcast_xml, "language"),
        copyrights=text(podcast_xml, "copyright"),
        itunes_author=text(podcast_xml, "itunes:author"),
        description=text(podcast_xml, "itunes:summary"),
        owner_email=text(podcast_xml, "itunes:email"),
        itunes_image=download_file(
            podcast_folder, text(podcast_xml.image, "url")
        ),
        itunes_category=attrs(podcast_xml, tag="itunes:category", atr="text"),
        subcategory=text(podcast_xml, "itunes:subcategory"),
        itunes_explicit=is_explicit(text(podcast_xml, "itunes:explicit")),
    )
    return podcast


def create_episode(pool: dict) -> Episode:
    episode_xml, podcast = (
        pool["e_xml"],
        pool["podcast"],
    )
    pub_date = dateparser.parse(text(episode_xml, "pubDate"))
    episode_folder = old_episode_folder_path(podcast.slug, pub_date)
    audio_url = attrs(episode_xml, tag="enclosure", atr="url").replace(
        "?media=rss", ""
    )
    episode = Episode.objects.create(
        podcast=podcast,
        title=text(episode_xml, "title"),
        description=text(episode_xml, "itunes:summary"),
        length=int(attrs(episode_xml, tag="enclosure", atr="length")),
        content_type=attrs(episode_xml, tag="enclosure", atr="type"),
        audio_file=download_file(episode_folder, audio_url),
        guid=text(episode_xml, "guid"),
        pub_date=pub_date,
        itunes_duration=text(episode_xml, "itunes:duration"),
        itunes_explicit=is_explicit(text(episode_xml, "itunes:explicit")),
    )
    return episode


class Command(BaseCommand):
    help = (
        "Example of using - "
        "manage.py downloadpodcast podcast-2 https://podster.fm/rss.xml?pid=36066"
        "Parse urls with iTunes RSS and save as Podcast and Episodes,"
        "addtionaly save all files (audio and covers). "
    )

    def add_arguments(self, parser):
        parser.add_argument("slug", help="Podcast RSS in iTunes format.")
        parser.add_argument("url", help="Podcast RSS in iTunes format.")

    def handle(self, *args, **options):
        podcast_xml = get_podcast_xml(options["url"])
        podcast = create_podcast(podcast_xml, options)
        episodes_xml = get_episodes_xml(options["url"])
        pool = []
        for e_xml in episodes_xml:
            pool.append(
                {"e_xml": e_xml, "podcast": podcast, "options": options}
            )

        with PoolExecutor(max_workers=4) as executor:
            for _ in executor.map(create_episode, pool):
                pass
