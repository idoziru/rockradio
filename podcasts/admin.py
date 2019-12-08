from django.contrib import admin
from django.utils.html import format_html
from podcasts.models import Podcast, Episode


class EpisodeInline(admin.TabularInline):
    model = Episode
    can_delete = False
    fields = (
        "title",
        "pub_date",
    )
    readonly_fields = (
        "title",
        "pub_date",
    )
    show_change_link = True


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ["title", "irunes_rss_url", "google_rss_url"]
    readonly_fields = ["folder_name", "slug"]

    def irunes_rss_url(self, obj):
        return format_html(
            "<a href='/podcasts/{url}-itunes.rss'>iTunes RSS</a>", url=obj.slug
        )

    def google_rss_url(self, obj):
        return format_html(
            "<a href='/podcasts/{url}-google.rss'>Google RSS</a>", url=obj.slug
        )

    inlines = [
        EpisodeInline,
    ]

    save_on_top = True


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    readonly_fields = ["guid", "length", "itunes_duration", "content_type"]
    date_hierarchy = "pub_date"
    list_display = ["podcast", "title", "pub_date", "itunes_duration"]
    list_filter = ["pub_date", "podcast"]
    search_fields = ["title"]
    list_display_links = ["title"]
    save_on_top = True
