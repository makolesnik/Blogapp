import hashlib
from django.db import models
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from tagging.fields import TagField
from tagging.models import Tag


SHORT_TEXT_LEN = 255

class Entry(models.Model):
    title = models.CharField(max_length=500)
    author = models.ForeignKey('auth.user')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    slug = models.SlugField(default='', editable=False)
    tags = TagField()
    
    def save(self, *args, **kwargs):
	self.slug = slugify(self.title)
	super(Entry, self).save(*args, **kwargs)

    def get_tags(self):
        return Tag.objects.get_for_object(self)

    def get_absolute_url(self):
	kwargs = {'year': self.created_at.year,
		  'month': self.created_at.month,
		  'day' : self.created_at.day,
		  'slug': self.slug,
		  'pk': self.pk}

	return reverse('entry_detail', kwargs=kwargs)
	#return reverse('entry_detail', kwargs={'pk': self.pk})

    def get_short_text(self):
	if len(self.body) > SHORT_TEXT_LEN:
	    return self.body[:SHORT_TEXT_LEN]
	else:
	    return self.body

    def __str__(self):
	return self.title

    class Meta:
	verbose_name_plural = "entries"


class Comment(models.Model):
    entry = models.ForeignKey(Entry)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)  

    def gravatar_url(self):
	md5 = hashlib.md5(self.email.encode())
	digest = md5.hexdigest()
	return 'http://www.gravatar.com/avatar/{}'.format(digest)

    def __str__(self):
	return self.body

    class Meta:
	verbose_name_plural = "comments"
	ordering = ('-modified_at',)
