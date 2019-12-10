from django.contrib import admin
from statistic.models import Spider


@admin.register(Spider)
class SpiderAdmin(admin.ModelAdmin):
    readonly_fields = ("name", "visits_counter")
    list_display = ("name", "visits_counter")
    orderring = ("visits_counter",)
