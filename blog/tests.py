from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Entry

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

class EntryViewTest(TestCase):

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