from collections import Counter
from django.db import models
from django.dispatch import receiver


class Spider(models.Model):
    name = models.CharField(blank=False, unique=True, max_length=255)
    visits_counter = models.IntegerField(default=0)

    @property
    def get_visits_count(self) -> int:
        """
        Returns:
            int: how much visits has made this Spider.
        """
        return self.visits.count()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.visits_counter = self.get_visits_count
        super(Spider, self).save(*args, **kwargs)


class Visit(models.Model):
    spider = models.ForeignKey(
        Spider,
        on_delete=models.CASCADE,
        related_name="visits",
        blank=True,
        null=True,
    )
    rss = models.CharField(blank=False, max_length=255)
    user_agent = models.CharField(blank=True, max_length=255)
    remote_addrr = models.CharField(blank=True, max_length=255)
    remote_host = models.CharField(blank=False, max_length=255)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        if self.spider:
            return self.spider.name
        else:
            return self.remote_addrr

    class Meta:
        ordering = ["-date"]

