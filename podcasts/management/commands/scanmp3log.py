import re
from datetime import datetime
from dateutil import parser as dateparser
from django.core.management.base import BaseCommand
from django.conf import settings
from statistic.models import Listening
from podcasts.models import Episode


IP_PATTERN = r"src=\"([\S]+)\""
DATE_PATTERN = r"time_local=[\"]{1}([\S]+\s[\S]+)[\"]{1}"
LENGHT_PATTERN = r"bytes_out=[\"]{1}([\S][\S]+)[\"]{1}"
AUDIO_FILE_PATTERN = r"uri_path=[\"]{1}\S+\/([\d]+\.mp3)[\"]{1}"
USER_AGENT_PATTER = r"http_user_agent=[\"]{1}([\S\s]+)[\"]{1}[\s]{1}uri_path"


def to_datetime(_str: str) -> datetime:
    return dateparser.parse(_str, fuzzy=True)


def find_or_default(line: str, pattern: str, default) -> str:
    group = re.findall(pattern, line)
    return group[0] if group else default


class Command(BaseCommand):
    help = (
        "Read nginx log file with information "
        "about access to all .mp3 files. Add this statistic to DB. "
        "You are able to point a path and a name for log file. "
        "By default it is defined in settings.base as "
        "os.path.join(BASE_DIR, 'logs', 'mp3_access.log' "
    )

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
                ip = find_or_default(line, IP_PATTERN, "0.0.0.0")
                pub_date = find_or_default(
                    line, DATE_PATTERN, str(datetime.now()),
                )
                length = int(find_or_default(line, LENGHT_PATTERN, 0))
                audio_file = find_or_default(line, AUDIO_FILE_PATTERN, None)
                user_agent = find_or_default(line, USER_AGENT_PATTER, "")
                if audio_file:
                    episode = Episode.get_episode(audio_file)
                    if episode is not None:
                        listening = Listening.objects.get_or_create(
                            episode=episode,
                            ip=ip,
                            pub_date=to_datetime(pub_date).date(),
                            audio_file=audio_file,
                            user_agent=user_agent,
                        )[0]
                        listening.length += length
                        listening.save()
                        episode.update_listenings_stat()

        with open(options["path_to_log"], "w") as f:
            f.write("")
