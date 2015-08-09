from django.contrib.syndication.views import Feed
from .models import Entry


class LatestPosts(Feed):
    title = "My blog"
    link = "/feed/"
    description = "Latest entries"

    def items(self):
	return Entry.objects.all().order_by('-modified_at')[:5]

