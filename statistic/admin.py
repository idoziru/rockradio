from rangefilter.filter import DateRangeFilter
from django.contrib import admin
from statistic.models import Listening


class ListeningInline(admin.TabularInline):
    model = Listening
    fields = ("episode", "ip", "pub_date")
    readonly_fields = ("episode", "ip", "pub_date")
    can_delete = False
    show_change_link = False


@admin.register(Listening)
class ListeningAdmin(admin.ModelAdmin):

    readonly_fields = ("episode", "ip", "pub_date", "length")
    list_display = ("episode", "ip", "pub_date")
    orderring = ("pub_date",)
    list_filter = (
        ("pub_date", DateRangeFilter),
        ("episode__pub_date", DateRangeFilter),
        "episode__podcast__title",
    )

    date_hierarchy = "pub_date"

