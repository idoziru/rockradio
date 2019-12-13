from django.contrib import admin
from statistic.models import Spider, Visit, Requester


class VisitInline(admin.TabularInline):
    model = Visit
    fields = ("remote_addrr", "remote_host", "rss", "date")
    readonly_fields = ("remote_addrr", "remote_host", "rss", "date")
    can_delete = False
    show_change_link = True


@admin.register(Spider)
class SpiderAdmin(admin.ModelAdmin):
    inlines = [
        VisitInline,
    ]
    readonly_fields = ("name", "visits_counter")
    list_display = ("name", "visits_counter")
    orderring = ("visits_counter",)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("remote_addrr", "remote_host", "rss", "date")
    list_filter = ("spider", "date", "rss")
    date_hierarchy = "date"

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.register(Requester)
class RequesterAdmin(admin.ModelAdmin):

    readonly_fields = ("name", "rss", "visits_counter")
    list_display = ("name", "rss", "visits_counter")
    orderring = ("visits_counter",)
    list_filter = ("rss",)
