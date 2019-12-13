import re
from datetime import datetime
from dateutil import parser as dateparser
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from statistic.models import Listening
from podcasts.models import Episode


def to_datetime(_str: str) -> datetime:
    return dateparser.parse(_str, fuzzy=True)


class Command(BaseCommand):
    help = ""

    def __init__(self):
        self.listenings = []
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument(
            "path_to_log",
            nargs="?",
            type=str,
            default=settings.LISTENING_LOG_PATH,
            help="",
        )

    def handle(self, *args, **options):
        with open(options["path_to_log"], "r") as f:
            for line in f.readlines():
                _ip = re.findall(r"src=\"([\S]+)\"", line)
                _pub_date = re.findall(
                    r"time_local=[\"]{1}([\S]+\s[\S]+)[\"]{1}", line,
                )
                _length = re.findall(
                    r"bytes_out=[\"]{1}([\S][\S]+)[\"]{1}", line
                )
                _audio_file = re.findall(
                    r"uri_path=[\"]{1}\S+\/([\d]+\.mp3)[\"]{1}", line
                )
                if _audio_file:
                    episode = Episode.get_episode(_audio_file[0])
                    if episode is not None:
                        listening = Listening.objects.get_or_create(
                            episode=episode,
                            ip=_ip[0] if _ip else "0.0.0.0",
                            pub_date=to_datetime(_pub_date[0]).date()
                            if _pub_date
                            else datetime.now(tz=timezone.utc),
                            audio_file=_audio_file[0] if _audio_file else None,
                        )[0]
                        length = int(_length[0] if _length else 0)
                        listening.length += length
                        listening.save()
