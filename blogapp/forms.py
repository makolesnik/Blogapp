from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Comment


class CommentForm(forms.ModelForm):

    class Meta:
	model = Comment
	fields = ('name', 'email', 'body')
	labels = {
		'name': _("Your name* :"),
		'email': _("E-mail (your email address will not be published)* :"),
		'body': _("Enter your comment here* :"),
	}
	error_messages = {
		'name': {
		    'required': _("Name is required.")},
                'email': {
                    'required': _("E-mail is required.")},
                'body': {
                    'required': _("Text is required.")},
	}

    def __init__(self, *args, **kwargs):
        self.entry = kwargs.pop('entry')
	super(CommentForm, self).__init__(*args, **kwargs)

    def save(self):
	comment = super(CommentForm, self).save(commit=False)
	comment.entry = self.entry
	comment.save()
	return comment
