import shutil
import os
from datetime import timedelta
from mutagen.mp3 import MP3
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from podcasts.utils import upload_podcast_files, upload_episode_files
from statistic.models import Listening


class Podcast(models.Model):
    """
    Read first - "A podcaster’s guide to RSS"
    https://help.apple.com/itc/podcasts_connect/#/itcb54353390
    """

    title = models.CharField(
        blank=False,
        max_length=255,
        help_text=("The show title"),
        verbose_name="Podcast title",
    )
    # TODO Все HTML вставки нужно автоматически оборачивать в ![CDATA[ ]]
    description = models.TextField(
        blank=True, max_length=4000, help_text=("The show description"),
    )
    # IMPROVE Make a checker for size and MBs
    itunes_image = models.FileField(
        blank=False,
        upload_to=upload_podcast_files,
        help_text=(
            "from 1400х1400 to 3000x3000 pixels, JPEG or PNG format, 72 dpi, "
            "not be larger than 512 KB."
        ),
    )
    language = models.CharField(
        max_length=8,
        default="ru-ru",
        blank=False,
        help_text=(
            "Use  ISO 639 list (two-letter language codes, with some "
            "possible modifiers, such as 'en-us')."
        ),
    )
    itunes_category = models.CharField(
        blank=False,
        max_length=255,
        help_text=(
            "The show category information. For a complete list of categories "
            "see Apple Podcasts categories."
        ),
    )
    itunes_explicit = models.BooleanField(
        default=False,
        blank=False,
        help_text=("The podcast parental advisory information."),
    )

    itunes_author = models.CharField(
        blank=False, max_length=255, help_text=("John Doe")
    )
    link = models.URLField(
        blank=True, help_text=("The website associated with a podcast")
    )

    owner_email = models.EmailField(
        blank=False,
        max_length=100,
        help_text=(
            "Use this tag to specify "
            "contact information for the podcast owner."
        ),
    )

    copyrights = models.CharField(
        blank=False,
        max_length=100,
        help_text="&#x2117; &amp; &#xA9; 2019 2capitals.space",
    )

    subcategory = models.CharField(
        blank=True,
        max_length=255,
        help_text=(
            "The show category information. For a complete list of "
            "subcategories, see Apple Podcasts categories."
        ),
    )

    slug = models.CharField(max_length=255, unique=True)
    folder_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class Episode(models.Model):
    podcast = models.ForeignKey(
        Podcast, on_delete=models.PROTECT, related_name="episodes"
    )

    title = models.CharField(
        blank=False,
        max_length=255,
        help_text=("An episode title."),
        verbose_name="Episode title",
    )
    audio_file = models.FileField(
        blank=False,
        upload_to=upload_episode_files,
        help_text=(
            "The URL attribute points to your podcast media file. "
            "in .mp3 format"
        ),
    )
    length = models.BigIntegerField(
        blank=True,
        null=True,
        help_text=("The length attribute is the file size in bytes."),
    )
    content_type = models.CharField(
        blank=False,
        max_length=255,
        default="audio/mpeg",
        help_text=(
            "The type attribute provides the correct category for the type "
            "of file you are using. The type values for the supported file formats are: "
            "audio/x-m4a, audio/mpeg, video/quicktime, video/mp4, video/x-m4v, "
            "application/pdf, and document/x-epub"
        ),
    )

    guid = models.CharField(
        blank=True,
        max_length=255,
        help_text=(
            "Every item tag (episode) should have a permanent, "
            "case-sensitive globally unique identifier (GUID). "
            "When you add episodes to your RSS feed, GUIDs are compared"
            "in case-sensitive fashion to determine which episodes are new. "
            "If you don’t add the GUID for an episode, the episode URL "
            "is used instead. Assign the GUID to an episode only once "
            "and never change it. Assigning new GUIDs to existing episodes "
            "can cause issues with your podcast’s listing and chart placement "
            "in the iTunes Store."
        ),
    )
    pub_date = models.DateTimeField(
        blank=False,
        auto_now=False,
        auto_now_add=False,
        verbose_name="Episode pub date",
        help_text=(
            "The pub_date tag specifies the date and time "
            "when an episode was released. Format the content using "
            "the RFC 2822 specifications. "
            "For example: Wed, 15 Jun 2014 19:00:00 GMT."
        ),
    )
    description = models.TextField(
        blank=True, help_text=("An episode description."),
    )
    itunes_duration = models.CharField(
        blank=False,
        max_length=8,
        help_text=(
            "The content you specify in the itunes:duration tag "
            "appears in the Time column in the List View on the iTunes Store. "
            "Specify one of the following formats for the itunes:duration "
            "tag value: HH:MM:SS, H:MM:SS, MM:SS, M:SS"
        ),
    )
    link = models.URLField(blank=True, help_text=("An episode link URL."))
    itunes_explicit = models.BooleanField(
        default=False,
        help_text=(
            "The itunes:explicit tag indicates whether your podcast "
            "contains explicit material."
        ),
    )

    more_then_1_min = models.BigIntegerField(
        default=0, help_text=("Listenings more then 1 min.")
    )

    more_then_5_min = models.BigIntegerField(
        default=0, help_text=("Listenings more then 5 min.")
    )

    more_then_10_min = models.BigIntegerField(
        default=0, help_text=("Listenings more then 10 min.")
    )

    more_then_20_min = models.BigIntegerField(
        default=0, help_text=("Listenings more then 20 min.")
    )

    @staticmethod
    def get_episode(audio_file):
        episodes = Episode.objects.filter(audio_file__contains=audio_file)
        if episodes:
            return episodes[0]
        return None

    @classmethod
    def get_duration(cls, episode) -> str:
        audio = MP3(episode.audio_file.path)
        seconds = int(audio.info.length)
        return str(timedelta(seconds=seconds))

    def get_more_then_20_min(self) -> int:
        """Return count of listenings of the current episode
        if a listeting >= 20 minutues. 1 minut ~= 1000000 bytes.
        """
        minute = 1000000
        return len(
            Listening.objects.filter(episode=self, length__gte=minute * 20)
        )

    def get_more_then_10_min(self) -> int:
        """Return count of listenings of the current episode
        if a listeting >= 10 minutues. 1 minut ~= 1000000 bytes.
        """
        minute = 1000000
        return len(
            Listening.objects.filter(episode=self, length__gte=minute * 10)
        )

    def get_more_then_5_min(self) -> int:
        """Return count of listenings of the current episode
        if a listeting >= 5 minutues. 1 minut ~= 1000000 bytes.
        """
        minute = 1000000
        return len(
            Listening.objects.filter(episode=self, length__gte=minute * 5)
        )

    def get_more_then_1_min(self) -> int:
        """Return count of listenings of the current episode
        if a listeting >= 1 minutues. 1 minut ~= 1000000 bytes.
        """
        minute = 1000000
        return len(
            Listening.objects.filter(episode=self, length__gte=minute * 1)
        )

    def update_listenings_stat(self):
        Episode.objects.filter(pk=self.pk).update(
            more_then_1_min=self.get_more_then_1_min(),
            more_then_5_min=self.get_more_then_5_min(),
            more_then_10_min=self.get_more_then_10_min(),
            more_then_20_min=self.get_more_then_20_min(),
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-pub_date"]

    def save(self, *args, **kwargs):
        try:
            this = Episode.objects.get(id=self.id)
            # deleting previous podcast audio file
            # before add new files
            if this.audio_file != self.audio_file:
                this.audio_file.delete(save=False)
        # all this exeptions need only for cases
        # when you download a new podcast from the old RSS feed
        # and you need manualy work with files via SFTP
        except (Episode.DoesNotExist, FileNotFoundError):
            pass
        super().save(*args, **kwargs)
        # IMPROVE Do only for new audio files
        duration = Episode.get_duration(self)
        Episode.objects.filter(pk=self.pk).update(itunes_duration=duration)


@receiver(models.signals.pre_save, sender=Podcast)
def delete_old_cover_file(sender, instance, **kwargs):
    try:
        old_img = Podcast.objects.get(pk=instance.pk).itunes_image
        new_img = instance.itunes_image
        if old_img != new_img:
            # deleting previous podcast img file before add new
            old_img.delete(save=False)
    # all this exeptions need only for cases
    # when you download a new podcast from the old RSS feed
    # and you need manualy work with files via SFTP
    except (Podcast.DoesNotExist, FileNotFoundError):
        pass


@receiver(models.signals.post_save, sender=Podcast)
def set_podcast_folder_name(sender, instance, **kwargs):
    if instance.folder_name == "":
        Podcast.objects.filter(pk=instance.pk).update(
            folder_name=instance.slug
        )


@receiver(models.signals.pre_delete, sender=Podcast)
def delete_podcast_folder(sender, instance, **kwargs):
    path = os.path.join(settings.MEDIA_ROOT, instance.folder_name)
    # deleting podcast folder with all files
    shutil.rmtree(path, ignore_errors=True)


@receiver(models.signals.post_save, sender=Episode)
def file_size(sender, instance, **kwargs) -> bool:
    """
    Returns:
            bool: if file size in bytes was correctly counted
    """
    if not instance.audio_file.path:
        return False
    length = os.path.getsize(instance.audio_file.path)
    Episode.objects.filter(pk=instance.pk).update(length=length)
    return True


@receiver(models.signals.post_save, sender=Episode)
def set_unique_guid(sender, instance, **kwargs):
    """Uses episode.audiofile to set episode.guid and do it only once,
       because it is important for iTunes not to change guid"""
    if not instance.guid:
        Episode.objects.filter(pk=instance.pk).update(guid=instance.audio_file)


@receiver(models.signals.pre_delete, sender=Episode)
def delete_episode_mp3(sender, instance, **kwargs):
    try:
        if instance.audio_file:
            instance.audio_file.delete(save=False)
    except FileNotFoundError:
        pass
