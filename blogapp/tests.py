from django.test import TestCase
from django_webtest import WebTest
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
import datetime
from django.contrib.auth import get_user_model
from django.template import Template, Context

from .models import Entry, Comment
from .views import HomeView
from .forms import CommentForm


class EntryModelTest(TestCase):
    
    def test_string_representation(self):
	entry = Entry(title="My entry title")
	self.assertEqual(str(entry), entry.title, "Entry title is " + str(entry) + " instead of " + entry.title)

    def test_verbose_name_plural(self):
	self.assertEqual(str(Entry._meta.verbose_name_plural), "entries")

    def test_get_absolute_url(self):
	user = get_user_model().objects.create(username='some_user')
	entry = Entry.objects.create(title='My entry title', author=user)
	self.assertIsNotNone(entry.get_absolute_url())

    def test_count_entry_objects(self):
	user = get_user_model().objects.create(username='some_user')
	self.assertEqual(Entry.objects.count(), 0)
	entry = Entry.objects.create(title='My entry title', author=user)
	self.assertEqual(Entry.objects.count(), 1)
	entry1 = Entry.objects.create(title='My entry title 2', author=user)
	self.assertEqual(Entry.objects.count(), 2)

class CommentModelTest(TestCase):
   
    def test_string_representation(self):
	comment = Comment(body="My comment body")
	self.assertEqual(str(comment), "My comment body")

    def test_verbose_name_plural(self):
	self.assertEqual(str(Comment._meta.verbose_name_plural), "comments")

    def test_count_comment_objects(self):
	user = get_user_model().objects.create(username='some_user')
	entry = Entry.objects.create(title="1-title", body="1-body", author=user)
	self.assertEqual(Comment.objects.count(), 0)
	comment = Comment.objects.create(body="My comment body", entry=entry)
	self.assertEqual(Comment.objects.count(), 1)
	comment2 = Comment.objects.create(body="My comment body 2", entry=entry)
	self.assertEqual(Comment.objects.count(), 2)

    def test_gravatar_url(self):

	comment = Comment(body="My comment body", name="saga", email="saga9119@gmail.com")
	expected = "http://www.gravatar.com/avatar/48480e427496ccf9fb1ebbd8fca8ff63"
	self.assertEqual(comment.gravatar_url(), expected)


class HomePageTests(TestCase):

    def setUp(self):
	self.user = get_user_model().objects.create(username='some_user')

    def test_one_entry(self):
	Entry.objects.create(title="1-title", body="1-body", author=self.user)
	response = self.client.get('/')
	self.assertContains(response, "1-title")
	self.assertContains(response, "1-body")

    def test_two_entries(self):
	Entry.objects.create(title="1-title", body="1-body", author=self.user)
	Entry.objects.create(title="2-title", body="2-body", author=self.user)
	response = self.client.get('/')
	self.assertContains(response, "1-title")
	self.assertContains(response, "1-body")
	self.assertContains(response, "2-title")
	self.assertContains(response, "2-body")	

    def test_no_entries(self):
	response = self.client.get('/')
	self.assertContains(response, "No blog entries yet.")
        
    def test_comments_is_present_on_the_homepage(self):
	entry = Entry.objects.create(title="1-title", body="1-body", author=self.user)
	response = self.client.get('/')
	self.assertContains(response, "comment(s)")	

    def test_no_no_comments(self):
	entry = Entry.objects.create(title="1-title", body="1-body", author=self.user)
	response = self.client.get(entry.get_absolute_url())
	self.assertContains(response, "No comments yet.")


class EntryViewTest(WebTest):
    
    def setUp(self):
	self.user = get_user_model().objects.create(username='some_user')
	self.entry = Entry.objects.create(title='1-title', body='1-body', author=self.user)

    def test_basic_view(self):
	response = self.client.get(self.entry.get_absolute_url())
	self.assertEqual(response.status_code, 200)

    def test_view_page(self):
	page = self.app.get(self.entry.get_absolute_url())
	self.assertEqual(len(page.forms), 1)
	self.assertContains(page, "* Indicates required field.")
	self.assertContains(page, "Your name* :")
	self.assertContains(page, "E-mail (your email address will not be published)* :")
	self.assertContains(page, "Enter your comment here* :")
	self.assertContains(page, "Create Comment")

    def test_form_error(self):
	page = self.app.get(self.entry.get_absolute_url())
	page = page.form.submit()
	self.assertContains(page, "is required.")

    def test_valid_form(self):
	page = self.app.get(self.entry.get_absolute_url())
	page.form['name'] = "Philipp"
	page.form['email'] = "phillip@example.com"
	page.form['body'] = "Test comment body."
	page = page.form.submit()
	self.assertRedirects(page, 
			self.entry.get_absolute_url()+"#comments")

    def test_url(self):
	title = "This is my test title"
	today = datetime.date.today()
	entry = Entry.objects.create(title=title, body="body", 
				     author=self.user)
	slug = slugify(title)

	url_short = "/{pk}/".format(pk=entry.pk)
	url_long = "/{year}/{month}/{day}/{pk}-{slug}/".format(
	    year = today.year,
	    month = today.month,
	    day = today.day,
	    slug = slug,
	    pk = entry.pk,
	)	
	response = self.client.get(url_long)
	_response = self.client.get(url_short)

	self.assertEqual(response.status_code, 200)
	self.assertEqual(_response.status_code, 200)

	self.assertTemplateUsed(
		response, template_name='entry_detail.html')
        self.assertTemplateUsed(
		_response, template_name='entry_detail.html')


    def test_misdated_url(self):
	entry = Entry.objects.create(
		title="title", body="body", author=self.user)
	url = "/0000/00/00/{0}-misdated/".format(entry.id)
	response = self.client.get(url)
	self.assertEqual(response.status_code, 200)
	self.assertTemplateUsed(
		response, template_name='entry_detail.html')

    def test_invalid_url(self):
	response = self.client.get("/0000/00/00/0-invalid/")
	self.assertEqual(response.status_code, 404)


class CommentFormTest(TestCase):
    def setUp(self):
	user = get_user_model().objects.create_user('zoidberg')
	self.entry = Entry.objects.create(author=user, title="My entry title")

    def test_init(self):
	CommentForm(entry=self.entry)

    def test_init_without_entry(self):
	with self.assertRaises(KeyError):
	    CommentForm()

    def test_valid_data(self):
	form = CommentForm({
	    'name': "Turanga Leela",
	    'email': "leela@example.com",
	    'body': "Hi there",
	}, entry=self.entry)
	self.assertTrue(form.is_valid())
	comment = form.save()
	self.assertEqual(comment.name, "Turanga Leela")
	self.assertEqual(comment.email, "leela@example.com")
	self.assertEqual(comment.body, "Hi there")
	self.assertEqual(comment.entry, self.entry)

    def test_blank_data(self):
	form = CommentForm({}, entry=self.entry)
	self.assertFalse(form.is_valid())
	self.assertEqual(form.errors, {
	    'name': [u"Name is required."],
	    'email': [u"E-mail is required."],
	    'body': [u"Text is required."],
	})

class EntryHistoryTag(TestCase):
    
    TEMPLATE = Template("{% load blogapp_tags %} {% entry_history %}")

    def setUp(self):
	self.user = get_user_model().objects.create(username="zoidberg")
	
    def test_entry_shows_up(self):
	entry = Entry.objects.create(author=self.user, title="My entry title")
	rendered = self.TEMPLATE.render(Context({}))
	self.assertIn(entry.title, rendered)

    def test_no_posts(self):
	rendered = self.TEMPLATE.render(Context({}))
	self.assertIn("No recent entries.", rendered)	

    def test_many_posts(self):
	for n in range(6):
	    Entry.objects.create(author=self.user, 
				title="Post #{0}".format(n))
	rendered = self.TEMPLATE.render(Context({}))
	self.assertIn("Post #5", rendered)
	self.assertNotIn("Post #6", rendered)



