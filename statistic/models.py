from django.db import models


class Listening(models.Model):
    episode = models.ForeignKey(
        "podcasts.Episode",
        on_delete=models.CASCADE,
        related_name="listenings",
        blank=False,
        null=False,
    )
    ip = models.CharField(blank=True, max_length=255)
    pub_date = models.DateTimeField(
        blank=True, verbose_name="Date of listening"
    )
    audio_file = models.FileField(blank=False)
    length = models.BigIntegerField(blank=True, default=0)
    user_agent = models.CharField(blank=True, max_length=3000, default="")

    def __str__(self):
        return str(self.ip)

    def __repr__(self):
        return self.__str__()
