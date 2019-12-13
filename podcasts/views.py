import os
from django.views.generic.detail import DetailView, TemplateResponseMixin
from django.conf import settings
from podcasts.models import Podcast
from statistic.models import Spider, Visit, Requester

# IMPROVE Static rss feeds and do not always dynamically generate it.


class ITunesRSSView(DetailView, TemplateResponseMixin):
    """
    Note, that template takes according to the url.
    - /podcasts/podcast-1-itunes.rss - will take template itunes.rss
    - /podcasts/podcast-1-google.rss - will take template goole.rss
    and so on.

    It  works automatically.
    """

    model = Podcast
    content_type = "application/xml"
    template_name = "itunes.rss"

    def get_context_object_name(self, obj):
        return "podcast"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_template_names(self):
        all_templates = []
        for template_dir in settings.TEMPLATES[0]["DIRS"]:
            for _dir, _dirnames, filenames in os.walk(template_dir):
                for filename in filenames:
                    all_templates.append(os.path.join(_dir, filename))
        current_template = f"{self.kwargs['rss_type']}.rss"
        if any(current_template in t for t in all_templates):
            return f"{self.kwargs['rss_type']}.rss"
        return self.template_name

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        rss = self.kwargs["rss_type"] or "Unrecognized"
        visit = Visit.objects.create(
            rss=self.kwargs["rss_type"],
            user_agent=request.META.get("USER_AGENT", "None"),
            remote_addrr=request.META.get("REMOTE_ADDR", "None"),
            remote_host=request.META.get("REMOTE_HOST", "None"),
        )
        spider = Spider.objects.get_or_create(name=rss)[0]
        requester = Requester.objects.get_or_create(
            name=request.META.get("REMOTE_ADDR", "None"), rss=rss
        )[0]
        requester.visits_counter += 1
        visit.spider = spider
        visit.save()
        spider.save()
        requester.save()
        return self.render_to_response(context)
