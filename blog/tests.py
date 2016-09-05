from django.test import TestCase
from django.contrib.auth import get_user_model
from django.template import Template, Context
from django.template.defaultfilters import slugify

from django_webtest import WebTest

import hashlib
import datetime

from .forms import CommentForm
from .models import Entry, Comment

class EntryModelTest(TestCase):

	def test_string_representation(self):
		entry = Entry(title="My entry title")
		self.assertEqual(str(entry), entry.title)

	def test_verbose_name_plural(self):
		self.assertEqual(str(Entry._meta.verbose_name_plural), "entries")

	def test_get_absolute_url(self):
		user = get_user_model().objects.create(username="armin")
		entry = Entry.objects.create(title="My entry title", author=user)
		self.assertIsNotNone(entry.get_absolute_url())


class ProjectTests(TestCase):

	def test_homepage(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)


class HomePageTests(TestCase):

    """Test whether our blog entries show up on the homepage"""

    def setUp(self):
        self.user = get_user_model().objects.create(username='some_user')

    def test_one_entry(self):
        Entry.objects.create(title='title', body='body', author=self.user)
        response = self.client.get('/')
        self.assertContains(response, 'title')
        self.assertContains(response, 'body')

    def test_two_entries(self):
        Entry.objects.create(title='title', body='body', author=self.user)
        Entry.objects.create(title='title', body='body', author=self.user)
        response = self.client.get('/')
        self.assertContains(response, 'title')
        self.assertContains(response, 'body')
        self.assertContains(response, 'title')

    def test_no_entries(self):
	    response = self.client.get('/')
	    self.assertContains(response, 'No blog entries yet.')

class EntryViewTest(WebTest):

	def setUp(self):
		self.user = get_user_model().objects.create(username="armin")
		self.entry = Entry.objects.create(title="title1", body="body1", author=self.user)

	def test_basic_view(self):
		response = self.client.get(self.entry.get_absolute_url())
		self.assertEqual(response.status_code, 200)

	def test_title_in_entry(self):
		response = self.client.get(self.entry.get_absolute_url())
		self.assertContains(response, self.entry.title)

	def test_body_in_entry(self):
		response = self.client.get(self.entry.get_absolute_url())
		self.assertContains(response, self.entry.body)

	def test_comment_in_entry(self):
		self.comment = Comment.objects.create(entry=self.entry, body="this is a test comment.")
		response = self.client.get(self.entry.get_absolute_url())
		self.assertContains(response, self.comment.body)

	def test_view_page(self):
		page = self.app.get(self.entry.get_absolute_url())
		self.assertEqual(len(page.forms), 1)

	def test_form_error(self):
		page = self.app.get(self.entry.get_absolute_url())
		page = page.form.submit()
		self.assertContains(page, "This field is required.")

	def test_form_success(self):
		page = self.app.get(self.entry.get_absolute_url())
		page.form['name'] = "Armin"
		page.form['email'] = "armin@gmail.com"
		page.form['body'] = "Test comment body."
		page = page.form.submit()
		self.assertRedirects(page, self.entry.get_absolute_url())

	def test_url(self):
		title = "This is the title"
		today = datetime.date.today()
		entry = Entry.objects.create(title=title, body="body", author=self.user)
		slug = slugify(title)
		url = "/{year}/{month}/{day}/{pk}-{slug}/".format(
			year = today.year,
			month = today.month,
			day = today.day,
			slug = slug,
			pk = entry.pk,
			)
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, template_name = 'blog/entry_detail.html')

	def test_misdated_url(self):
		entry = Entry.objects.create(title="title", body="body", author=self.user)
		url = "/0000/00/00/{0}-misdated/".format(entry.id)
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, template_name='blog/entry_detail.html')

	def test_invalid_url(self):
		entry = Entry.objects.create(title="title", body="body", author=self.user)
		response = self.client.get("/0000/00/00/0-invalid/")
		self.assertEqual(response.status_code, 404)


class CommentModelTest(TestCase):

	def test_string_representation(self):
		comment = Comment(email="armin@gmail.com")
		self.assertEqual(str(comment), "armin@gmail.com")

	def test_gravatar_url(self):
		email = "armin@gmail.com"
		comment = Comment(body="Comment Body", email=email)
		md5 = hashlib.md5(email.encode())
		digest = md5.hexdigest()
		expected = "http://www.gravatar.com/avatar/{}".format(digest)

class CommentFormTest(TestCase):

	def setUp(self):
		user = get_user_model().objects.create_user('armin')
		self.entry = Entry.objects.create(author=user, title="Entry Title")

	def test_init(self):
		CommentForm(entry=self.entry)

	def test_init_without_entry(self):
		with self.assertRaises(KeyError):
			CommentForm()
	
	def test_valid_date(self):
		form = CommentForm({
			'name' : "armin",
			'email' : "armin@gmail.com",
			'body' : "Hello There",
		}, entry=self.entry)
		self.assertTrue(form.is_valid())
		comment = form.save()
		self.assertEqual(comment.name, "armin")
		self.assertEqual(comment.email, "armin@gmail.com")
		self.assertEqual(comment.body, "Hello There")
		self.assertEqual(comment.entry, self.entry)

	# def test_blank_data(self):
	# 	form = CommentForm({}, entry=self.entry)
	# 	self.assertFalse(form.is_valid())
	# 	self.assertEqual(form.errors, {
	# 		'name' : ['This[17 chars]d.'],
	# 		'email' : ['required'],
	# 		'body' : ['This field is required.'],
	# 		})
		
class EntryHistoryTagTest(TestCase):
	TEMPLATE = Template("{% load blog_tags %} {% entry_history %}")

	def setUp(self):
		self.user = get_user_model().objects.create(username="armin")

	def test_entry_shows_up(self):
		entry = Entry.objects.create(author=self.user, title="My entry title")
		rendered = self.TEMPLATE.render(Context())
		self.assertIn(entry.title, rendered)

	def test_no_posts(self):
		rendered = self.TEMPLATE.render(Context({}))
		self.assertIn("No recent entries", rendered)

	def test_many_posts(self):
		for n in range(6):
			Entry.objects.create(author=self.user, title="Post #{0}".format(n))
		rendered = self.TEMPLATE.render(Context({}))
		self.assertIn("Post #5", rendered)
		self.assertNotIn("Post #6", rendered)

