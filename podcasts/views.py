import os
from django.views.generic.detail import DetailView, TemplateResponseMixin
from django.template.exceptions import TemplateDoesNotExist
from django.conf import settings
from podcasts.models import Podcast
from statistic.models import Spider

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
            for dir, dirnames, filenames in os.walk(template_dir):
                for filename in filenames:
                    all_templates.append(os.path.join(dir, filename))
        current_template = f"{self.kwargs['rss_type']}.rss"
        if any(current_template in t for t in all_templates):
            return f"{self.kwargs['rss_type']}.rss"
        else:
            return self.template_name

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        spider = Spider.objects.get_or_create(
            name=self.kwargs["rss_type"] or "Unrecognized"
        )[0]
        spider.visits_counter += 1
        spider.save()
        return self.render_to_response(context)
